"""
Ponto de entrada do Job tb_gm3_tailor_proposal.
"""

from __future__ import annotations

from config.args_resolver import resolve_job_args
from config.glue_context_factory import GlueContextFactory
from config.settings import Settings
from jobs.job_runner import JobDependencies, JobRunner
from readers.dynamodb_reader import DynamoDBReader
from services.dataframe_service import DataFrameService
from services.execution_date_service import ExecutionDateService
from services.parameter_store_service import ParameterStoreService
from writers.mesh_writer import MeshTarget, MeshWriter



REQUIRED_ARGS = [
    "JOB_NAME",
    "AWS_REGION",
    "DYNAMODB_TABLE",
    "DATABASE_NAME_WRITE",
    "TABLE_NAME_WRITE",
    "EXECUTION_PARAMETER",
]


def main() -> None:
    args = resolve_job_args(REQUIRED_ARGS)

    settings = Settings.from_args(args)

    spark, _, job = GlueContextFactory.create(args)

    deps = JobDependencies(
        spark=spark,
        parameter_store=ParameterStoreService(
            region_name=settings.aws_region,
            endpoint_url=settings.aws_endpoint_url,
        ),
        execution_date_service=ExecutionDateService(),
        dynamodb_reader=DynamoDBReader(
            region_name=settings.aws_region,
            table_name=settings.dynamodb_table,
            endpoint_url=settings.aws_endpoint_url,
            gsi_name=settings.dynamodb_gsi_name,
            partition_key_name=settings.dynamodb_partition_key_name,
            partition_key_value=settings.dynamodb_partition_key_value,
            sort_key_name=settings.dynamodb_sort_key_name,
            enable_incremental=settings.enable_incremental,
        ),
        dataframe_service=DataFrameService(),
        mesh_writer=MeshWriter(
            target=MeshTarget(
                database_name=settings.database_name_write,
                table_name=settings.table_name_write,
            ),
            write_mode=settings.mesh_write_mode,
            output_location=settings.mesh_output_location,
        ),
        enable_incremental=settings.enable_incremental,
        incremental_comparison_mode=(
            settings.incremental_comparison_mode
        ),
        job=job,
    )

    runner = JobRunner(deps)

    try:
        runner.execute(
            execution_parameter=settings.execution_parameter,
        )
    finally:
        spark.stop()


if __name__ == "__main__":
    main()
