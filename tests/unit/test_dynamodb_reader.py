from readers.dynamodb_reader import DynamoDBReader


class FakeDynamoClient:
    def __init__(self, gsi_active: bool) -> None:
        self.gsi_active = gsi_active
        self.query_calls = 0
        self.scan_calls = 0

    def describe_table(self, TableName: str) -> dict:
        gsis = []
        if self.gsi_active:
            gsis.append(
                {
                    "IndexName": "gsi_startAt",
                    "IndexStatus": "ACTIVE",
                }
            )

        return {"Table": {"GlobalSecondaryIndexes": gsis}}

    def query(self, **_: object) -> dict:
        self.query_calls += 1
        return {
            "Items": [
                {
                    "proposalID": {"S": "p-002"},
                    "startAt": {"S": "20260618"},
                }
            ]
        }

    def scan(self, **_: object) -> dict:
        self.scan_calls += 1
        return {
            "Items": [
                {
                    "proposalID": {"S": "p-001"},
                    "startAt": {"S": "20260615"},
                }
            ]
        }


def test_read_items_uses_query_when_gsi_is_active(
    monkeypatch,
) -> None:
    fake_client = FakeDynamoClient(gsi_active=True)

    monkeypatch.setattr(
        "readers.dynamodb_reader.boto3.client",
        lambda *args, **kwargs: fake_client,
    )

    reader = DynamoDBReader(
        region_name="sa-east-1",
        table_name="tb_gm3_tailor_proposal",
        enable_incremental=True,
    )

    items = reader._read_items("20260617")

    assert fake_client.query_calls == 1
    assert fake_client.scan_calls == 0
    assert items[0]["proposalID"] == "p-002"


def test_read_items_falls_back_to_scan_when_gsi_is_missing(
    monkeypatch,
) -> None:
    fake_client = FakeDynamoClient(gsi_active=False)

    monkeypatch.setattr(
        "readers.dynamodb_reader.boto3.client",
        lambda *args, **kwargs: fake_client,
    )

    reader = DynamoDBReader(
        region_name="sa-east-1",
        table_name="tb_gm3_tailor_proposal",
        enable_incremental=True,
    )

    items = reader._read_items("20260617")

    assert fake_client.query_calls == 0
    assert fake_client.scan_calls == 1
    assert items[0]["proposalID"] == "p-001"

