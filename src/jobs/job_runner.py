"""
Orquestra o fluxo completo do Job.
"""

from __future__ import annotations

from dataclasses import dataclass
from time import perf_counter
from typing import Optional, Protocol

from botocore.exceptions import ClientError
from pyspark.sql import SparkSession

from constants.dynamodb import (
    DYNAMODB_COLUMNS_AFTER_RENAME,
    RENAME_COLUMNS_MAPPING,
)
from constants.tables import PARTITIONS_TABLE
from services.dataframe_service import DataFrameService
from services.execution_date_service import ExecutionDateService
from services.parameter_store_service import ParameterStoreService
from utils.dates import current_execution_date
from utils.logger import get_logger
from writers.mesh_writer import MeshWriter
from readers.dynamodb_reader import DynamoDBReader


class CommitableJob(Protocol):
    def commit(self) -> None: ...


@dataclass(frozen=True)
class JobDependencies:
    spark: SparkSession
    parameter_store: ParameterStoreService
    execution_date_service: ExecutionDateService
    dynamodb_reader: DynamoDBReader
    dataframe_service: DataFrameService
    mesh_writer: MeshWriter
    enable_incremental: bool
    incremental_comparison_mode: str
    job: Optional[CommitableJob] = None


class JobRunner:
    """
    Executa o fluxo do Job garantindo:
    - FULL quando não há data válida no Parameter Store
    - Atualização do parâmetro apenas em sucesso
    - Commit do Job apenas em sucesso
    """

    def __init__(self, deps: JobDependencies) -> None:
        self._deps = deps
        self._logger = get_logger(self.__class__.__name__)

    def execute(
        self,
        execution_parameter: str,
    ) -> None:
        start = perf_counter()
        self._logger.info("Início do Job")

        last_execution = self._safe_get_last_execution(execution_parameter)

        cutoff_date_for_reader = (
            self._deps.execution_date_service.get_cutoff_date(
                last_execution=last_execution,
                comparison_mode=(
                    self._deps.incremental_comparison_mode
                ),
            )
        )

        if self._deps.enable_incremental and cutoff_date_for_reader:
            self._logger.info(
                "Modo INCREMENTAL habilitado com corte %s",
                cutoff_date_for_reader,
            )
        else:
            self._logger.info("Modo FULL (Scan completo)")

        df = self._deps.dynamodb_reader.read_as_dataframe(
            spark=self._deps.spark,
            execution_date=cutoff_date_for_reader,
        )

        df = self._deps.dataframe_service.rename_columns(
            df,
            RENAME_COLUMNS_MAPPING,
        )

        df = self._deps.dataframe_service.select_columns(
            df,
            DYNAMODB_COLUMNS_AFTER_RENAME,
        )

        execution_date = current_execution_date()

        df = self._deps.dataframe_service.add_execution_partition(
            df,
            execution_date,
        )

        records_read = df.count()
        self._logger.info("Registros lidos: %s", records_read)

        self._deps.mesh_writer.write(
            dataframe=df,
            partitions=PARTITIONS_TABLE,
            ordered_columns=DYNAMODB_COLUMNS_AFTER_RENAME,
            mode="append",
        )

        self._deps.parameter_store.update_parameter(
            parameter_name=execution_parameter,
            value=execution_date,
        )

        if self._deps.job:
            self._deps.job.commit()

        elapsed = perf_counter() - start
        self._logger.info(
            "Fim do Job (sucesso). Tempo: %.2fs",
            elapsed,
        )

    def _safe_get_last_execution(
        self,
        execution_parameter: str,
    ) -> Optional[str]:
        try:
            return self._deps.parameter_store.get_parameter(
                execution_parameter
            )
        except ClientError as exc:
            self._logger.info(
                "Falha ao ler parâmetro %s; forçando FULL. Erro: %s",
                execution_parameter,
                exc,
            )
            return None
