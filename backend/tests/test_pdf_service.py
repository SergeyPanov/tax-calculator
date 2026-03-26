from decimal import Decimal

from backend.services.pdf_service import PdfService


def test_parse_value_strips_currency_suffix() -> None:
    service = PdfService()

    assert service._parse_value("45 000 Kč") == Decimal("45000")
    assert service._parse_value("45\xa0000 Kč") == Decimal("45000")
    assert service._parse_value("45000") == Decimal("45000")
