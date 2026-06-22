from services.execution_date_service import ExecutionDateService


def test_is_full_load_when_none() -> None:
    assert ExecutionDateService.is_full_load(None) is True


def test_is_full_load_when_blank() -> None:
    assert ExecutionDateService.is_full_load("") is True
    assert ExecutionDateService.is_full_load("   ") is True


def test_is_full_load_when_has_value() -> None:
    assert ExecutionDateService.is_full_load("20260618") is False


def test_get_execution_date() -> None:
    assert ExecutionDateService.get_execution_date(None) is None
    assert ExecutionDateService.get_execution_date("   ") is None
    assert ExecutionDateService.get_execution_date("20260618") == "20260618"


def test_get_cutoff_date_with_gt_plus_1_day() -> None:
    assert (
        ExecutionDateService.get_cutoff_date(
            "20260618",
            "gt_plus_1_day",
        )
        == "20260619"
    )


def test_get_cutoff_date_with_gte() -> None:
    assert (
        ExecutionDateService.get_cutoff_date(
            "20260618",
            "gte",
        )
        == "20260618"
    )
