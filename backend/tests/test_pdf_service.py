from decimal import Decimal

import pytest

from backend.services.pdf_service import PdfService


def test_parse_value_strips_currency_suffix() -> None:
    service = PdfService()

    assert service._parse_value("45 000 Kč") == Decimal("45000")
    assert service._parse_value("45\xa0000 Kč") == Decimal("45000")
    assert service._parse_value("45000") == Decimal("45000")


def test_extract_from_tables_handles_utf8_czech_diacritics() -> None:
    service = PdfService()
    tables: list[list[list[str | None]]] = [
        [
            [None, "Úhrn zúčtovaných příjmů ze závislé činnosti", "1 234 567 Kč"],
            ["2.", "Příjmy vyplacené do 31. ledna", "1 000 000 Kč"],
            ["3.", "Zúčtováno v měsících", "01 02 03"],
            ["4.", "Doplatky příjmů podle § 5 odst. 4 zákona", "234 567 Kč"],
        ]
    ]

    data = service._extract_from_tables(tables)

    assert data["total_accounted_incomes"] == Decimal("1234567")
    assert data["incomes_paid_till_january_31"] == Decimal("1000000")
    assert data["accounted_in_months"] == "01 02 03"
    assert data["additional_payments"] == Decimal("234567")


def test_extract_from_tables_preserves_dd_mm_yyyy_date_format_in_row_3() -> None:
    service = PdfService()
    tables: list[list[list[str | None]]] = [
        [
            ["3.", "Zúčtováno v měsících", "31.01.2025"],
        ]
    ]

    data = service._extract_from_tables(tables)

    assert data["accounted_in_months"] == "31.01.2025"


@pytest.mark.parametrize(
    "vat_label",
    [
        "Příjmy včetně DPH 21 %",
        "Příjmy včetně DPH 12 %",
        "Příjmy včetně DPH 0 %",
    ],
)
def test_extract_from_tables_handles_vat_rate_labels(vat_label: str) -> None:
    service = PdfService()
    tables: list[list[list[str | None]]] = [
        [
            ["2.", vat_label, "100 000 Kč"],
        ]
    ]

    data = service._extract_from_tables(tables)

    assert data["incomes_paid_till_january_31"] == Decimal("100000")
