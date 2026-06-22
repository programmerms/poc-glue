"""
Centraliza todos os parâmetros recebidos pelo Glue Job.
"""

from dataclasses import dataclass
from typing import Dict, Optional


@dataclass(frozen=True)
class Settings:
    """
    Representa os parâmetros recebidos pelo Glue Job.
    """

    job_name: str

    aws_region: str
    aws_endpoint_url: Optional[str]

    dynamodb_table: str
    dynamodb_gsi_name: str
    dynamodb_partition_key_name: str
    dynamodb_partition_key_value: str
    dynamodb_sort_key_name: str

    database_name_write: str

    table_name_write: str

    execution_parameter: str
    mesh_output_location: Optional[str]
    mesh_write_mode: str
    enable_incremental: bool
    incremental_comparison_mode: str

    @classmethod
    def from_args(cls, args: Dict[str, str]) -> "Settings":
        """
        Cria uma instância de Settings utilizando
        os argumentos do Glue Job.
        """

        return cls(
            job_name=args["JOB_NAME"],
            aws_region=args["AWS_REGION"],
            aws_endpoint_url=args.get("AWS_ENDPOINT_URL"),
            dynamodb_table=args["DYNAMODB_TABLE"],
            dynamodb_gsi_name=args.get(
                "DYNAMODB_GSI_NAME",
                "gsi_startAt",
            ),
            dynamodb_partition_key_name=args.get(
                "DYNAMODB_PARTITION_KEY_NAME",
                "staticPartitionKey",
            ),
            dynamodb_partition_key_value=args.get(
                "DYNAMODB_PARTITION_KEY_VALUE",
                "TAILOR",
            ),
            dynamodb_sort_key_name=args.get(
                "DYNAMODB_SORT_KEY_NAME",
                "startAt",
            ),
            database_name_write=args["DATABASE_NAME_WRITE"],
            table_name_write=args["TABLE_NAME_WRITE"],
            execution_parameter=args["EXECUTION_PARAMETER"],
            mesh_output_location=args.get("MESH_OUTPUT_LOCATION"),
            mesh_write_mode=args.get("MESH_WRITE_MODE", "catalog"),
            enable_incremental=_to_bool(
                args.get("ENABLE_INCREMENTAL", "false")
            ),
            incremental_comparison_mode=args.get(
                "INCREMENTAL_COMPARISON_MODE",
                "gt_plus_1_day",
            ),
        )


def _to_bool(value: str) -> bool:
    return value.strip().lower() in {"1", "true", "yes", "on"}
