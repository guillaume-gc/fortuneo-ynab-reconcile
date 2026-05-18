from pathlib import Path

import pytest

from main import Transaction, parse_fortuneo, parse_ynab, reconcile

FIXTURES = Path(__file__).parent / "fixtures"


def fortuneo(name: str) -> list[Transaction]:
    return parse_fortuneo((FIXTURES / f"fortuneo_credit_copy_{name}.txt").read_text())


def ynab(name: str) -> list[Transaction]:
    return parse_ynab(FIXTURES / f"ynab_credit_export_{name}.csv")


class TestParseFortuneo:
    def test_parses_transactions(self):
        result = fortuneo("equal")
        assert result == [
            Transaction(label="CARTE XXXX LABEL", amount=200.0),
            Transaction(label="CARTE XXXX LABEL", amount=20.0),
        ]

    def test_parses_duplicates(self):
        result = fortuneo("duplicate")
        assert result == [
            Transaction(label="CARTE XXXX LABEL", amount=200.0),
            Transaction(label="CARTE XXXX LABEL", amount=20.0),
            Transaction(label="CARTE XXXX LABEL", amount=20.0),
        ]


class TestParseYnab:
    def test_parses_transactions(self):
        result = ynab("equal")
        assert result == [
            Transaction(label="XXX_31.05.2026_XXXX_XXX", amount=200.0),
            Transaction(label="XXX_31.05.2026_XXXX_XXX", amount=20.0),
        ]

    def test_parses_duplicates(self):
        result = ynab("duplicate")
        assert result == [
            Transaction(label="XXX_31.05.2026_XXXX_XXX", amount=200.0),
            Transaction(label="XXX_31.05.2026_XXXX_XXX", amount=20.0),
            Transaction(label="XXX_31.05.2026_XXXX_XXX", amount=20.0),
        ]


class TestReconcile:
    def test_all_matched(self):
        missing, errors = reconcile(fortuneo("equal"), ynab("equal"))
        assert missing == []
        assert errors == []

    def test_ynab_missing_payee(self):
        # Fortuneo has €200 + €20, YNAB only has €200 → YNAB is missing €20
        missing, errors = reconcile(fortuneo("equal"), ynab("missing"))
        assert len(missing) == 1
        assert missing[0].amount == 20.0
        assert errors == []

    def test_ynab_orphan_payee(self):
        # Fortuneo has €200, YNAB has €200 + €20 → YNAB has an orphan €20
        missing, errors = reconcile(fortuneo("missing"), ynab("equal"))
        assert missing == []
        assert len(errors) == 1
        assert errors[0].amount == 20.0

    def test_duplicates_all_matched(self):
        missing, errors = reconcile(fortuneo("duplicate"), ynab("duplicate"))
        assert missing == []
        assert errors == []

    def test_duplicate_ynab_missing_one(self):
        # Fortuneo has €200 + €20 + €20, YNAB has €200 + €20 → YNAB missing one €20
        missing, errors = reconcile(fortuneo("duplicate"), ynab("equal"))
        assert len(missing) == 1
        assert missing[0].amount == 20.0
        assert errors == []

    def test_duplicate_ynab_orphan_one(self):
        # Fortuneo has €200 + €20, YNAB has €200 + €20 + €20 → YNAB has orphan €20
        missing, errors = reconcile(fortuneo("equal"), ynab("duplicate"))
        assert missing == []
        assert len(errors) == 1
        assert errors[0].amount == 20.0
