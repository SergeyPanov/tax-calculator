from decimal import Decimal
from io import BytesIO
from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient

from main import app
from models.confirmation_of_a_taxable_income import ConfirmationOfATaxableIncome


@pytest.fixture
def client() -> TestClient:
    return TestClient(app)


def _mock_confirmation(**kwargs: Decimal | None) -> ConfirmationOfATaxableIncome:
    return ConfirmationOfATaxableIncome(
        tax_base=kwargs.get("tax_base", Decimal("1000000")),
        total_tax_advance=kwargs.get("advance", Decimal("150000")),
    )


class TestCalculateTaxEndpoint:
    def test_valid_pdf(self, client: TestClient) -> None:
        """Upload a single PDF — should return TaxResult with one confirmation."""
        confirmation = _mock_confirmation(
            tax_base=Decimal("900000"), advance=Decimal("135000")
        )

        with patch(
            "routers.pdf.PdfService.extract_confirmation_of_tax_income",
            return_value=confirmation,
        ):
            files = {"file": ("employer.pdf", BytesIO(b"%PDF-fake"), "application/pdf")}
            resp = client.post("/calculate-tax", files=files)

        assert resp.status_code == 200
        body = resp.json()
        assert len(body["confirmations"]) == 1
        assert Decimal(body["aggregated_tax_base"]) == Decimal("900000")
        assert "total_tax" in body
        assert "overpayment_or_underpayment" in body

    def test_non_pdf_file_rejected(self, client: TestClient) -> None:
        """A non-PDF upload should return 400."""
        files = {"file": ("doc.txt", BytesIO(b"hello"), "text/plain")}
        resp = client.post("/calculate-tax", files=files)
        assert resp.status_code == 400
        assert "not a PDF" in resp.json()["detail"]

    def test_existing_upload_pdf_unaffected(self, client: TestClient) -> None:
        """The old single-PDF endpoint still works."""
        confirmation = _mock_confirmation()

        with patch(
            "routers.pdf.PdfService.extract_confirmation_of_tax_income",
            return_value=confirmation,
        ):
            files = {"file": ("invoice.pdf", BytesIO(b"%PDF-fake"), "application/pdf")}
            resp = client.post("/upload-pdf", files=files)

        assert resp.status_code == 200
        assert "tax_base" in resp.json()
