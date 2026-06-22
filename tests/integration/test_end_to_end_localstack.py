import os

import boto3
import pytest
from pyspark.sql import SparkSession

from jobs.job_runner import JobDependencies, JobRunner
from readers.dynamodb_reader import DynamoDBReader
from services.dataframe_service import DataFrameService
from services.execution_date_service import ExecutionDateService
from services.parameter_store_service import ParameterStoreService
from writers.mesh_writer import MeshTarget, MeshWriter


@pytest.fixture()
def spark() -> SparkSession:
    spark = (
        SparkSession.builder.master("local[1]")
        .appName("glue-poc-tests")
        .getOrCreate()
    )
    yield spark
    spark.stop()


@pytest.mark.integration
def test_end_to_end_full_and_incremental(
    spark: SparkSession,
    tmp_path,
    monkeypatch,
) -> None:
    endpoint_url = os.getenv("AWS_ENDPOINT_URL")
    if not endpoint_url:
        pytest.skip("AWS_ENDPOINT_URL não definido")

    region = os.getenv("AWS_REGION", "sa-east-1")
    table_name = os.getenv("DYNAMODB_TABLE", "tb_gm3_tailor_proposal")
    param_name = os.getenv(
        "EXECUTION_PARAMETER",
        "/local/tailor/glue-execution-date",
    )

    ssm = boto3.client("ssm", region_name=region, endpoint_url=endpoint_url)

    ssm.put_parameter(
        Name=param_name,
        Value=" ",
        Type="String",
        Overwrite=True,
    )

    monkeypatch.setattr(
        "jobs.job_runner.current_execution_date",
        lambda: "20260618",
    )

    output_1 = tmp_path / "mesh_full"

    deps = JobDependencies(
        spark=spark,
        parameter_store=ParameterStoreService(region, endpoint_url),
        execution_date_service=ExecutionDateService(),
        dynamodb_reader=DynamoDBReader(
            region_name=region,
            table_name=table_name,
            endpoint_url=endpoint_url,
            enable_incremental=True,
        ),
        dataframe_service=DataFrameService(),
        mesh_writer=MeshWriter(
            target=MeshTarget(
                database_name="local_db",
                table_name="local_table",
            ),
            write_mode="local",
            output_location=str(output_1),
        ),
        enable_incremental=True,
        incremental_comparison_mode="gt_plus_1_day",
        job=None,
    )

    JobRunner(deps).execute(
        execution_parameter=param_name,
    )

    value_1 = ssm.get_parameter(Name=param_name)["Parameter"]["Value"]
    assert value_1 == "20260618"

    rows_1 = spark.read.parquet(str(output_1)).select("proposalID").collect()
    ids_1 = {r["proposalID"] for r in rows_1}
    assert ids_1 == {"p-001", "p-002"}

    ssm.put_parameter(
        Name=param_name,
        Value="20260616",
        Type="String",
        Overwrite=True,
    )

    monkeypatch.setattr(
        "jobs.job_runner.current_execution_date",
        lambda: "20260619",
    )

    output_2 = tmp_path / "mesh_incremental"

    deps_2 = JobDependencies(
        spark=spark,
        parameter_store=ParameterStoreService(region, endpoint_url),
        execution_date_service=ExecutionDateService(),
        dynamodb_reader=DynamoDBReader(
            region_name=region,
            table_name=table_name,
            endpoint_url=endpoint_url,
            enable_incremental=True,
        ),
        dataframe_service=DataFrameService(),
        mesh_writer=MeshWriter(
            target=MeshTarget(
                database_name="local_db",
                table_name="local_table",
            ),
            write_mode="local",
            output_location=str(output_2),
        ),
        enable_incremental=True,
        incremental_comparison_mode="gt_plus_1_day",
        job=None,
    )

    JobRunner(deps_2).execute(
        execution_parameter=param_name,
    )

    value_2 = ssm.get_parameter(Name=param_name)["Parameter"]["Value"]
    assert value_2 == "20260619"

    rows_2 = spark.read.parquet(str(output_2)).select("proposalID").collect()
    ids_2 = {r["proposalID"] for r in rows_2}
    assert ids_2 == {"p-002"}
