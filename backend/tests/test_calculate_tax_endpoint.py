import io
import zipfile
from decimal import Decimal
from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient

from backend.main import app
from backend.models.confirmation_of_a_taxable_income import ConfirmationOfATaxableIncome


@pytest.fixture
def client() -> TestClient:
    return TestClient(app)


def _mock_confirmation(**kwargs: Decimal | None) -> ConfirmationOfATaxableIncome:
    tax_base = kwargs.get("tax_base", Decimal("1000000"))
    additional_payments = kwargs.get("additional_payments", Decimal("0"))
    return ConfirmationOfATaxableIncome(
        total_accounted_incomes=None,
        incomes_paid_till_january_31=kwargs.get("incomes", tax_base),
        accounted_in_months=None,
        additional_payments=additional_payments,
        tax_base=tax_base,
        tax_advance_from_row_2=None,
        tax_advance_from_row_4=None,
        total_tax_advance=kwargs.get("advance", Decimal("150000")),
        monthly_tax_bonuses=None,
    )


def _make_zip(pdf_entries: dict[str, bytes]) -> bytes:
    """Build an in-memory zip containing the given filename -> bytes mapping."""
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, mode="w") as zf:
        for name, data in pdf_entries.items():
            zf.writestr(name, data)
    return buf.getvalue()


class TestCalculateTaxEndpoint:
    def test_valid_zip_single_pdf(self, client: TestClient) -> None:
        """Upload a zip with one PDF -- should return TaxResult with one confirmation."""
        confirmation = _mock_confirmation(
            tax_base=Decimal("900000"), advance=Decimal("135000")
        )
        zip_bytes = _make_zip({"employer.pdf": b"%PDF-fake"})

        with patch(
            "backend.routers.pdf.PdfService.extract_confirmation_of_tax_income",
            return_value=confirmation,
        ):
            resp = client.post(
                "/calculate-tax",
                files={
                    "file": ("documents.zip", io.BytesIO(zip_bytes), "application/zip")
                },
            )

        assert resp.status_code == 200
        body = resp.json()
        assert len(body["confirmations"]) == 1
        assert Decimal(body["partial_tax_base"]) == Decimal("900000")
        assert Decimal(body["income_tax"]) == Decimal("135000")
        assert Decimal(body["tax_after_credits"]) == Decimal("104160")
        assert Decimal(body["advances_withheld"]) == Decimal("135000")
        assert "overpayment_or_underpayment" in body

    def test_non_zip_file_rejected(self, client: TestClient) -> None:
        """A non-zip upload should return 400."""
        resp = client.post(
            "/calculate-tax",
            files={"file": ("doc.txt", io.BytesIO(b"hello"), "text/plain")},
        )
        assert resp.status_code == 400
        assert "zip" in resp.json()["detail"].lower()

    def test_multiple_pdfs_in_zip_aggregated(self, client: TestClient) -> None:
        """Zip with multiple PDFs should aggregate values across all confirmations."""
        confirmations = [
            _mock_confirmation(tax_base=Decimal("900000")),
            _mock_confirmation(tax_base=Decimal("800000")),
        ]
        zip_bytes = _make_zip(
            {"employer-a.pdf": b"%PDF-a", "employer-b.pdf": b"%PDF-b"}
        )

        with patch(
            "backend.routers.pdf.PdfService.extract_confirmation_of_tax_income",
            side_effect=confirmations,
        ):
            resp = client.post(
                "/calculate-tax",
                files={
                    "file": ("documents.zip", io.BytesIO(zip_bytes), "application/zip")
                },
            )

        assert resp.status_code == 200
        body = resp.json()
        assert len(body["confirmations"]) == 2
        assert Decimal(body["aggregated_tax_base"]) == Decimal("1700000")

    def test_empty_zip_rejected(self, client: TestClient) -> None:
        """A zip with no PDF files should return 400."""
        zip_bytes = _make_zip({"readme.txt": b"no pdfs here"})
        resp = client.post(
            "/calculate-tax",
            files={"file": ("empty.zip", io.BytesIO(zip_bytes), "application/zip")},
        )
        assert resp.status_code == 400
        assert "No PDF" in resp.json()["detail"]

    def test_upload_pdf_endpoint_removed(self, client: TestClient) -> None:
        """The /upload-pdf endpoint should no longer exist (404)."""
        resp = client.post(
            "/upload-pdf",
            files={
                "file": ("invoice.pdf", io.BytesIO(b"%PDF-fake"), "application/pdf")
            },
        )
        assert resp.status_code == 404

    def test_confirmation_keeps_dd_mm_yyyy_text(self, client: TestClient) -> None:
        """Row-3 text values like DD.MM.YYYY must be preserved in response."""
        confirmation = ConfirmationOfATaxableIncome(
            total_accounted_incomes=None,
            incomes_paid_till_january_31=Decimal("500000"),
            accounted_in_months="31.01.2025",
            additional_payments=Decimal("0"),
            tax_base=Decimal("500000"),
            tax_advance_from_row_2=None,
            tax_advance_from_row_4=None,
            total_tax_advance=Decimal("75000"),
            monthly_tax_bonuses=None,
        )
        zip_bytes = _make_zip({"potvrzeni.pdf": b"%PDF-fake"})

        with patch(
            "backend.routers.pdf.PdfService.extract_confirmation_of_tax_income",
            return_value=confirmation,
        ):
            resp = client.post(
                "/calculate-tax",
                files={
                    "file": ("documents.zip", io.BytesIO(zip_bytes), "application/zip")
                },
            )

        assert resp.status_code == 200
        body = resp.json()
        assert body["confirmations"][0]["accounted_in_months"] == "31.01.2025"

    def test_dph_rate_named_pdfs_are_processed(self, client: TestClient) -> None:
        """Endpoint should process PDFs regardless of DPH rate naming patterns."""
        confirmations = [
            _mock_confirmation(tax_base=Decimal("210000")),
            _mock_confirmation(tax_base=Decimal("120000")),
            _mock_confirmation(tax_base=Decimal("0")),
        ]
        zip_bytes = _make_zip(
            {
                "faktura-dph-21.pdf": b"%PDF-21",
                "faktura-dph-12.pdf": b"%PDF-12",
                "faktura-dph-0.pdf": b"%PDF-0",
            }
        )

        with patch(
            "backend.routers.pdf.PdfService.extract_confirmation_of_tax_income",
            side_effect=confirmations,
        ):
            resp = client.post(
                "/calculate-tax",
                files={
                    "file": ("documents.zip", io.BytesIO(zip_bytes), "application/zip")
                },
            )

        assert resp.status_code == 200
        body = resp.json()
        assert len(body["confirmations"]) == 3
        assert Decimal(body["aggregated_tax_base"]) == Decimal("330000")

    def test_parse_error_mentions_utf8_filename(self, client: TestClient) -> None:
        """Parser failure detail should preserve UTF-8 Czech filename."""
        filename = "potvrzení-český.pdf"
        zip_bytes = _make_zip({filename: b"%PDF-fake"})

        with patch(
            "backend.routers.pdf.PdfService.extract_confirmation_of_tax_income",
            side_effect=Exception("broken pdf"),
        ):
            resp = client.post(
                "/calculate-tax",
                files={
                    "file": ("documents.zip", io.BytesIO(zip_bytes), "application/zip")
                },
            )

        assert resp.status_code == 400
        assert filename in resp.json()["detail"]
