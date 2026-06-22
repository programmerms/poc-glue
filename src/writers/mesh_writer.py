"""
Writer responsável por publicar dados no Data Mesh.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from pyspark.sql import DataFrame
from pyspark.sql.utils import AnalysisException


@dataclass(frozen=True)
class MeshTarget:
    """
    Identifica o destino lógico no Data Mesh.
    """

    database_name: str
    table_name: str


class MeshWriter:
    """
    Publica um DataFrame no Data Mesh.

    Modos suportados:
    - `catalog`: escrita oficial via `saveAsTable()`
    - `local`: escrita em Parquet particionado para debug e testes locais
    """

    def __init__(
        self,
        target: MeshTarget,
        write_mode: str,
        output_location: Optional[str] = None,
    ) -> None:
        self._target = target
        self._write_mode = write_mode
        self._output_location = output_location

    def write(
        self,
        dataframe: DataFrame,
        partitions: list[str],
        ordered_columns: Optional[list[str]] = None,
        mode: str = "append",
    ) -> None:
        """
        Publica o DataFrame conforme o modo configurado.

        Args:
            dataframe: DataFrame final.
            partitions: Lista de colunas de partição.
            ordered_columns: Ordem final das colunas (sem partições).
            mode: Modo de escrita do Spark.
        """

        df = self._order_columns(
            dataframe=dataframe,
            partitions=partitions,
            ordered_columns=ordered_columns,
        )

        if self._write_mode == "catalog":
            self._write_catalog(df, partitions, mode)
            return

        if self._write_mode == "local":
            self._write_local(df, partitions, mode)
            return

        raise ValueError(
            f"Modo de escrita não suportado: {self._write_mode}"
        )

    def _order_columns(
        self,
        dataframe: DataFrame,
        partitions: list[str],
        ordered_columns: Optional[list[str]],
    ) -> DataFrame:
        if not ordered_columns:
            return dataframe

        select_columns = [
            *ordered_columns,
            *[p for p in partitions if p not in ordered_columns],
        ]

        return dataframe.select(*select_columns)

    def _write_catalog(
        self,
        dataframe: DataFrame,
        partitions: list[str],
        mode: str,
    ) -> None:
        full_table_name = (
            f"{self._target.database_name}.{self._target.table_name}"
        )
        df = dataframe

        try:
            target_columns = (
                dataframe.sparkSession.table(full_table_name).columns
            )
            select_columns = [
                column
                for column in target_columns
                if column in dataframe.columns
            ]
            if select_columns:
                df = dataframe.select(*select_columns)
        except AnalysisException:
            # Em cenários locais ou de bootstrap sem catálogo disponível,
            # mantém a ordem já preparada pelo pipeline.
            df = dataframe

        (
            df.write.mode(mode)
            .format("hive")
            .partitionBy(*partitions)
            .saveAsTable(full_table_name)
        )

    def _write_local(
        self,
        dataframe: DataFrame,
        partitions: list[str],
        mode: str,
    ) -> None:
        if not self._output_location:
            raise ValueError(
                "MESH_OUTPUT_LOCATION é obrigatório em modo local"
            )

        (
            dataframe.write.mode(mode)
            .partitionBy(*partitions)
            .parquet(self._output_location)
        )
