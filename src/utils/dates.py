"""
Funções utilitárias relacionadas à manipulação de datas.
"""

from datetime import datetime, timedelta


DATE_PATTERN = "%Y%m%d"


def current_execution_date() -> str:
    """
    Retorna a data atual no formato YYYYMMDD.

    Returns:
        Data formatada.
    """

    return datetime.now().strftime(DATE_PATTERN)


def parse_execution_date(value: str) -> datetime:
    """
    Converte uma string YYYYMMDD em datetime.

    Args:
        value: Data no formato YYYYMMDD.

    Returns:
        datetime correspondente.
    """

    return datetime.strptime(value, DATE_PATTERN)


def add_days(value: str, days: int) -> str:
    """
    Adiciona dias a uma data no formato YYYYMMDD.

    Args:
        value: Data base no formato YYYYMMDD.
        days: Quantidade de dias a adicionar.

    Returns:
        Data resultante no mesmo formato.
    """

    return (
        parse_execution_date(value) + timedelta(days=days)
    ).strftime(DATE_PATTERN)
