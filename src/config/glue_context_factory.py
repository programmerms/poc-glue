"""
Factory responsável pela criação dos objetos principais do AWS Glue.

Centraliza a criação de:

- SparkSession
- GlueContext
- Job
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Optional

from pyspark.sql import SparkSession

from config.spark_config import SparkConfig


@dataclass
class LocalJob:
    def init(self, *_: Any, **__: Any) -> None:
        return None

    def commit(self) -> None:
        return None


class GlueContextFactory:
    """
    Factory responsável por inicializar o ambiente Glue.
    """

    @staticmethod
    def create(
        args: Dict[str, str],
    ) -> tuple[SparkSession, Optional[Any], Any]:
        """
        Inicializa SparkSession, GlueContext e Job.

        Args:
            args: Argumentos recebidos pelo Glue Job.

        Returns:
            tuple contendo:

            - SparkSession
            - GlueContext
            - Job
        """

        spark = SparkConfig.create()

        try:
            from awsglue.context import GlueContext  # type: ignore
            from awsglue.job import Job  # type: ignore

            glue_context = GlueContext(spark.sparkContext)
            job = Job(glue_context)
            job.init(args["JOB_NAME"], args)
            return spark, glue_context, job

        except ModuleNotFoundError:
            job = LocalJob()
            job.init(args.get("JOB_NAME", "local-job"), args)
            return spark, None, job

        except Exception:
            raise
