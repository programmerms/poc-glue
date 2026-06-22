"""
Utilitário responsável pela criação do logger da aplicação.
"""

import logging


def get_logger(name: str) -> logging.Logger:
    """
    Cria um logger padronizado.

    Args:
        name: Nome do logger.

    Returns:
        Logger configurado.
    """

    logger = logging.getLogger(name)

    if logger.handlers:
        return logger

    logger.setLevel(logging.INFO)

    formatter = logging.Formatter(
        "[%(asctime)s] "
        "[%(levelname)s] "
        "%(message)s"
    )

    handler = logging.StreamHandler()

    handler.setFormatter(formatter)

    logger.addHandler(handler)

    return logger