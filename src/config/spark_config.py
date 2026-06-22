"""
Responsável pela configuração da SparkSession utilizada pelo AWS Glue.

Centraliza todas as configurações do Spark para evitar que fiquem
espalhadas pelo projeto.
"""

from pyspark.sql import SparkSession


class SparkConfig:
    """
    Factory responsável por criar uma SparkSession configurada
    para execução no AWS Glue 4.0.
    """

    @staticmethod
    def create() -> SparkSession:
        """
        Cria uma SparkSession configurada para o ambiente Glue.

        Returns:
            SparkSession: Sessão Spark configurada.
        """

        return (
            SparkSession.builder
            .enableHiveSupport()
            .config("hive.exec.dynamic.partition.mode", "nonstrict")
            .config("hive.exec.dynamic.partition", "true")
            .config("spark.sql.files.ignoreCorruptFiles", "true")
            .config("spark.sql.parquet.enableVectorizedReader", "false")
            .config("spark.sql.parquet.mergeSchema", "true")
            .config(
                "spark.sql.parquet.datetimeRebaseModeInWrite",
                "LEGACY"
            )
            .getOrCreate()
        )