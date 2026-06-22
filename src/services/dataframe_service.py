"""
Serviço responsável pelas transformações do Spark DataFrame.
"""

from pyspark.sql import DataFrame
from pyspark.sql.functions import lit


class DataFrameService:
    """
    Centraliza todas as transformações do DataFrame.
    """

    @staticmethod
    def add_execution_partition(
        dataframe: DataFrame,
        execution_date: str
    ) -> DataFrame:
        """
        Adiciona a coluna de particionamento.

        Args:
            dataframe: DataFrame de entrada.
            execution_date: Data da execução.

        Returns:
            DataFrame transformado.
        """

        return dataframe.withColumn(
            "ano_mes_dia",
            lit(int(execution_date))
        )

    @staticmethod
    def select_columns(
        dataframe: DataFrame,
        columns: list[str]
    ) -> DataFrame:
        """
        Seleciona as colunas desejadas.

        Args:
            dataframe: DataFrame de entrada.
            columns: Colunas que serão mantidas.

        Returns:
            DataFrame transformado.
        """

        return dataframe.select(*columns)

    @staticmethod
    def rename_columns(
        dataframe: DataFrame,
        mapping: dict[str, str]
    ) -> DataFrame:
        """
        Renomeia colunas.

        Args:
            dataframe: DataFrame de entrada.
            mapping: Dicionário contendo
                     coluna_origem -> coluna_destino.

        Returns:
            DataFrame transformado.
        """

        for old_name, new_name in mapping.items():
            dataframe = dataframe.withColumnRenamed(
                old_name,
                new_name
            )

        return dataframe