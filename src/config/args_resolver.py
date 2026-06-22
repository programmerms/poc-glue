"""
Resolução de parâmetros do Job para execução no Glue e local.
"""

from __future__ import annotations

import os
from typing import Iterable

from config.env_loader import load_local_env_files
from utils.validations import is_blank


def resolve_job_args(
    required_keys: Iterable[str],
) -> dict[str, str]:
    """
    Resolve parâmetros do Job.

    Prioridade:
    1) Glue (getResolvedOptions), quando disponível
    2) Variáveis de ambiente
    """

    load_local_env_files()
    required = list(required_keys)

    try:
        from awsglue.utils import getResolvedOptions  # type: ignore

        import sys

        args = getResolvedOptions(sys.argv, required)

        return {key: str(value) for key, value in args.items()}

    except ModuleNotFoundError:
        resolved: dict[str, str] = {}

        for key in required:
            value = os.getenv(key)
            if is_blank(value):
                raise ValueError(
                    f"Variável obrigatória não definida: {key}"
                )
            resolved[key] = value.strip()

        optional_keys = [
            "AWS_ENDPOINT_URL",
            "MESH_OUTPUT_LOCATION",
            "MESH_WRITE_MODE",
            "ENABLE_INCREMENTAL",
            "INCREMENTAL_COMPARISON_MODE",
            "DYNAMODB_GSI_NAME",
            "DYNAMODB_PARTITION_KEY_NAME",
            "DYNAMODB_PARTITION_KEY_VALUE",
            "DYNAMODB_SORT_KEY_NAME",
        ]

        for key in optional_keys:
            value = os.getenv(key)
            if not is_blank(value):
                resolved[key] = value.strip()

        return resolved
