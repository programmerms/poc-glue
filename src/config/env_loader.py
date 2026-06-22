"""
Carregamento simples de arquivos `.env` para execução local.
"""

from __future__ import annotations

import os
from pathlib import Path


def load_local_env_files() -> None:
    """
    Carrega `.env` e `.env.local` quando presentes.

    Precedência:
    1) variáveis já existentes no ambiente
    2) `.env.local`
    3) `.env`
    """

    original_env_keys = set(os.environ.keys())

    _load_env_file(
        file_path=Path.cwd() / ".env",
        protected_keys=original_env_keys,
        allow_override=False,
    )
    _load_env_file(
        file_path=Path.cwd() / ".env.local",
        protected_keys=original_env_keys,
        allow_override=True,
    )


def _load_env_file(
    file_path: Path,
    protected_keys: set[str],
    allow_override: bool,
) -> None:
    if not file_path.exists():
        return

    for raw_line in file_path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()

        if not line or line.startswith("#") or "=" not in line:
            continue

        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip().strip("\"'")

        if not key or key in protected_keys:
            continue

        if allow_override or key not in os.environ:
            os.environ[key] = value
