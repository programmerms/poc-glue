"""
Bootstrap de recursos no LocalStack para POC local.
"""

from __future__ import annotations

import os
import time
from typing import Any

import boto3
from botocore.exceptions import ClientError

from config.env_loader import load_local_env_files


def _get_env(name: str, default: str) -> str:
    value = os.getenv(name)
    return value.strip() if value and value.strip() else default


def main() -> None:
    load_local_env_files()

    region = _get_env("AWS_REGION", "sa-east-1")
    endpoint_url = _get_env("AWS_ENDPOINT_URL", "http://localstack:4566")
    table_name = _get_env("DYNAMODB_TABLE", "tb_gm3_tailor_proposal")
    parameter_name = _get_env(
        "EXECUTION_PARAMETER",
        "/local/tailor/glue-execution-date",
    )

    dynamodb = boto3.client(
        "dynamodb",
        region_name=region,
        endpoint_url=endpoint_url,
    )

    ssm = boto3.client(
        "ssm",
        region_name=region,
        endpoint_url=endpoint_url,
    )

    _ensure_table(dynamodb, table_name)
    _ensure_parameter(ssm, parameter_name)
    _seed_items(dynamodb, table_name)


def _ensure_table(dynamodb: Any, table_name: str) -> None:
    try:
        dynamodb.describe_table(TableName=table_name)
        return
    except dynamodb.exceptions.ResourceNotFoundException:
        pass

    dynamodb.create_table(
        TableName=table_name,
        AttributeDefinitions=[
            {"AttributeName": "staticPartitionKey", "AttributeType": "S"},
            {"AttributeName": "proposalID", "AttributeType": "S"},
            {"AttributeName": "startAt", "AttributeType": "S"},
        ],
        KeySchema=[
            {"AttributeName": "staticPartitionKey", "KeyType": "HASH"},
            {"AttributeName": "proposalID", "KeyType": "RANGE"},
        ],
        BillingMode="PAY_PER_REQUEST",
        GlobalSecondaryIndexes=[
            {
                "IndexName": "gsi_startAt",
                "KeySchema": [
                    {"AttributeName": "staticPartitionKey", "KeyType": "HASH"},
                    {"AttributeName": "startAt", "KeyType": "RANGE"},
                ],
                "Projection": {"ProjectionType": "ALL"},
            }
        ],
    )

    for _ in range(30):
        status = dynamodb.describe_table(TableName=table_name)["Table"][
            "TableStatus"
        ]
        if status == "ACTIVE":
            return
        time.sleep(0.5)

    raise RuntimeError(f"Tabela {table_name} não ficou ACTIVE a tempo")


def _ensure_parameter(ssm: Any, parameter_name: str) -> None:
    try:
        ssm.get_parameter(Name=parameter_name)
        return
    except ssm.exceptions.ParameterNotFound:
        pass

    ssm.put_parameter(
        Name=parameter_name,
        Value=" ",
        Type="String",
        Overwrite=True,
    )


def _seed_items(dynamodb: Any, table_name: str) -> None:
    items = [
        {
            "staticPartitionKey": {"S": "TAILOR"},
            "proposalID": {"S": "p-001"},
            "clientdID": {"S": "c-001"},
            "clientType": {"S": "PF"},
            "deleted": {"BOOL": False},
            "functional": {"BOOL": True},
            "productDescription": {"S": "Produto A"},
            "productId": {"S": "prod-001"},
            "proposalSequence": {"N": "1"},
            "startAt": {"S": "20260615"},
            "#st": {"S": "CREATED"},
            "statusHubin": {"S": "OK"},
            "enviado": {"BOOL": True},
        },
        {
            "staticPartitionKey": {"S": "TAILOR"},
            "proposalID": {"S": "p-002"},
            "clientdID": {"S": "c-002"},
            "clientType": {"S": "PJ"},
            "deleted": {"BOOL": False},
            "functional": {"BOOL": True},
            "productDescription": {"S": "Produto B"},
            "productId": {"S": "prod-002"},
            "proposalSequence": {"N": "2"},
            "startAt": {"S": "20260618"},
            "#st": {"S": "APPROVED"},
            "statusHubin": {"S": "OK"},
            "enviado": {"BOOL": False},
        },
    ]

    for item in items:
        try:
            dynamodb.put_item(TableName=table_name, Item=item)
        except ClientError:
            raise


if __name__ == "__main__":
    main()
