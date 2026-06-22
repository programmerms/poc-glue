"""
Funções utilitárias para validação de parâmetros.
"""


def is_blank(value: str | None) -> bool:
    """
    Verifica se um valor é nulo ou vazio.

    Args:
        value: Valor a ser validado.

    Returns:
        True quando vazio.
    """

    return value is None or value.strip() == ""