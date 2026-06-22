from __future__ import annotations

DYNAMODB_COLUMNS_RAW: list[str] = [
    "proposalID",
    "clientdID",
    "clientType",
    "deleted",
    "functional",
    "productDescription",
    "productId",
    "proposalSequence",
    "startAt",
    "staticPartitionKey",
    "#st",
    "statusHubin",
    "enviado",
]

RENAME_COLUMNS_MAPPING: dict[str, str] = {
    "#st": "st",
}

DYNAMODB_COLUMNS_AFTER_RENAME: list[str] = [
    "proposalID",
    "clientdID",
    "clientType",
    "deleted",
    "functional",
    "productDescription",
    "productId",
    "proposalSequence",
    "startAt",
    "staticPartitionKey",
    "st",
    "statusHubin",
    "enviado",
]

