"""
Serviço responsável por decidir se a execução será FULL ou INCREMENTAL.
"""

from typing import Optional

from utils.dates import add_days
from utils.validations import is_blank


class ExecutionDateService:
    """
    Responsável por interpretar a última data de execução.
    """

    @staticmethod
    def is_full_load(last_execution: Optional[str]) -> bool:
        """
        Verifica se a execução deverá ser FULL LOAD.

        Args:
            last_execution: Data armazenada no Parameter Store.

        Returns:
            True quando deverá executar FULL LOAD.
        """

        return is_blank(last_execution)

    @staticmethod
    def get_execution_date(last_execution: Optional[str]) -> Optional[str]:
        """
        Retorna a data que será utilizada pelo Reader.

        Returns:
            None para FULL LOAD ou a data armazenada.
        """

        if ExecutionDateService.is_full_load(last_execution):
            return None

        return last_execution

    @staticmethod
    def get_cutoff_date(
        last_execution: Optional[str],
        comparison_mode: str,
    ) -> Optional[str]:
        """
        Retorna a data efetiva de corte conforme a estratégia configurada.

        Estratégias suportadas:
        - gte: utiliza a própria data armazenada
        - gt: utiliza a própria data armazenada
        - gt_plus_1_day: soma um dia à data armazenada
        """

        execution_date = ExecutionDateService.get_execution_date(
            last_execution
        )

        if execution_date is None:
            return None

        if comparison_mode == "gt_plus_1_day":
            return add_days(execution_date, 1)

        if comparison_mode in {"gte", "gt"}:
            return execution_date

        raise ValueError(
            f"Modo de comparação incremental não suportado: "
            f"{comparison_mode}"
        )
