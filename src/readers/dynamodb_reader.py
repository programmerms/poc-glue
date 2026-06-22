"""
Reader responsável pela leitura de dados no Amazon DynamoDB.
"""

from __future__ import annotations

from typing import Any, Optional

import boto3
from boto3.dynamodb.types import TypeDeserializer
from botocore.exceptions import ClientError
from pyspark.sql import DataFrame, SparkSession
from pyspark.sql.types import (
    BooleanType,
    LongType,
    StringType,
    StructField,
    StructType,
)

from utils.logger import get_logger


class DynamoDBReader:
    """
    Realiza leitura FULL (Scan) e prepara a estratégia INCREMENTAL.

    Estratégia:
    - quando incremental está desabilitado: sempre faz FULL Scan;
    - quando incremental está habilitado e há data de corte:
      - tenta Query via GSI, se existir e estiver ACTIVE;
      - caso contrário, faz fallback para Scan com filtro.
    """

    def __init__(
        self,
        region_name: str,
        table_name: str,
        endpoint_url: Optional[str] = None,
        gsi_name: str = "gsi_startAt",
        partition_key_name: str = "staticPartitionKey",
        partition_key_value: str = "TAILOR",
        sort_key_name: str = "startAt",
        enable_incremental: bool = False,
    ) -> None:
        self._client = boto3.client(
            "dynamodb",
            region_name=region_name,
            endpoint_url=endpoint_url,
        )
        self._table_name = table_name
        self._gsi_name = gsi_name
        self._partition_key_name = partition_key_name
        self._partition_key_value = partition_key_value
        self._sort_key_name = sort_key_name
        self._enable_incremental = enable_incremental
        self._deserializer = TypeDeserializer()
        self._logger = get_logger(self.__class__.__name__)

    def read_as_dataframe(
        self,
        spark: SparkSession,
        execution_date: Optional[str] = None,
    ) -> DataFrame:
        """
        Lê itens do DynamoDB e devolve um Spark DataFrame.

        Args:
            spark: SparkSession.
            execution_date: Data efetiva de corte no formato YYYYMMDD.

        Returns:
            DataFrame contendo os itens desserializados.
        """

        items = self._read_items(execution_date)

        if not items:
            return spark.createDataFrame([], _build_empty_schema())

        return spark.createDataFrame(items)

    def _read_items(
        self,
        execution_date: Optional[str],
    ) -> list[dict[str, Any]]:
        if not self._enable_incremental or execution_date is None:
            self._logger.info(
                "Leitura configurada para FULL Scan na tabela %s",
                self._table_name,
            )
            return self._scan_items()

        if self._gsi_is_active():
            try:
                self._logger.info(
                    "Executando Query incremental via GSI %s com corte %s",
                    self._gsi_name,
                    execution_date,
                )
                return self._query_items(execution_date)
            except ClientError as exc:
                self._logger.info(
                    "Falha ao consultar GSI %s; fallback para Scan. "
                    "Erro: %s",
                    self._gsi_name,
                    exc,
                )

        self._logger.info(
            "GSI indisponível; fallback para Scan com filtro em %s > %s",
            self._sort_key_name,
            execution_date,
        )
        return self._scan_items(execution_date)

    def _scan_items(
        self,
        execution_date: Optional[str] = None,
    ) -> list[dict[str, Any]]:
        last_evaluated_key: Optional[dict[str, Any]] = None
        results: list[dict[str, Any]] = []

        while True:
            kwargs: dict[str, Any] = {"TableName": self._table_name}

            if execution_date:
                kwargs.update(
                    {
                        "FilterExpression": (
                            f"{self._sort_key_name} > :startAt"
                        ),
                        "ExpressionAttributeValues": {
                            ":startAt": {"S": execution_date}
                        },
                    }
                )

            if last_evaluated_key:
                kwargs["ExclusiveStartKey"] = last_evaluated_key

            response = self._client.scan(**kwargs)

            results.extend(
                self._deserialize_items(response.get("Items", []))
            )

            last_evaluated_key = response.get("LastEvaluatedKey")

            if not last_evaluated_key:
                break

        return results

    def _query_items(
        self,
        execution_date: str,
    ) -> list[dict[str, Any]]:
        last_evaluated_key: Optional[dict[str, Any]] = None
        results: list[dict[str, Any]] = []

        while True:
            kwargs: dict[str, Any] = {
                "TableName": self._table_name,
                "IndexName": self._gsi_name,
                "KeyConditionExpression": (
                    f"{self._partition_key_name} = :pk "
                    f"AND {self._sort_key_name} > :startAt"
                ),
                "ExpressionAttributeValues": {
                    ":pk": {"S": self._partition_key_value},
                    ":startAt": {"S": execution_date},
                },
            }

            if last_evaluated_key:
                kwargs["ExclusiveStartKey"] = last_evaluated_key

            response = self._client.query(**kwargs)

            results.extend(
                self._deserialize_items(response.get("Items", []))
            )

            last_evaluated_key = response.get("LastEvaluatedKey")

            if not last_evaluated_key:
                break

        return results

    def _gsi_is_active(self) -> bool:
        try:
            response = self._client.describe_table(
                TableName=self._table_name
            )
        except ClientError as exc:
            self._logger.info(
                "Falha ao descrever tabela %s para verificar GSI. "
                "Erro: %s",
                self._table_name,
                exc,
            )
            return False

        gsis = response.get("Table", {}).get(
            "GlobalSecondaryIndexes",
            [],
        )

        for gsi in gsis:
            if gsi.get("IndexName") == self._gsi_name:
                return gsi.get("IndexStatus") == "ACTIVE"

        return False

    def _deserialize_items(
        self,
        items: list[dict[str, Any]],
    ) -> list[dict[str, Any]]:
        parsed: list[dict[str, Any]] = []

        for item in items:
            parsed.append(
                {
                    key: self._deserializer.deserialize(value)
                    for key, value in item.items()
                }
            )

        return parsed


def _build_empty_schema() -> StructType:
    return StructType(
        [
            StructField("proposalID", StringType(), True),
            StructField("clientdID", StringType(), True),
            StructField("clientType", StringType(), True),
            StructField("deleted", BooleanType(), True),
            StructField("functional", BooleanType(), True),
            StructField("productDescription", StringType(), True),
            StructField("productId", StringType(), True),
            StructField("proposalSequence", LongType(), True),
            StructField("startAt", StringType(), True),
            StructField("staticPartitionKey", StringType(), True),
            StructField("#st", StringType(), True),
            StructField("statusHubin", StringType(), True),
            StructField("enviado", BooleanType(), True),
        ]
    )
