import zipfile
from io import BytesIO

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile

from backend.models.confirmation_of_a_taxable_income import ConfirmationOfATaxableIncome
from backend.models.tax_result import TaxResult
from backend.services.pdf_service import PdfService
from backend.services.tax_calculation_service import TaxCalculationService

router = APIRouter()


def get_pdf_service() -> PdfService:
    return PdfService()


def get_tax_calculation_service() -> TaxCalculationService:
    return TaxCalculationService()


@router.post("/calculate-tax")
async def calculate_tax(
    file: UploadFile = File(...),
    pdf_service: PdfService = Depends(get_pdf_service),
    tax_service: TaxCalculationService = Depends(get_tax_calculation_service),
) -> TaxResult:
    """Parse POZP PDFs from a zip archive and calculate annual DPFO income tax (DAP-compliant).

    Accepts a .zip file containing one or more Potvrzeni o zdanitelnych prijmech (MFin 5460)
    PDF files. Each PDF is extracted and parsed; results are aggregated and tax is calculated:
    - Tax base rounded down to nearest 100 CZK (DAP r. 56)
    - Progressive income tax: 15% up to ANNUAL_THRESHOLD_CZK, 23% above (DAP r. 57)
    - Sleva na poplatnika (CZK 30,840) applied automatically (DAP r. 70)
    - Tax after credits (DAP r. 71)
    - Overpayment/underpayment vs. withheld advances (DAP r. 84)

    Args:
        file: Uploaded .zip archive containing PDF files.
        pdf_service: PDF parsing service (dependency-injected).
        tax_service: Tax calculation service (dependency-injected).

    Returns:
        TaxResult with DAP-aligned fields and calculated tax.

    Raises:
        HTTPException(400): If file is not a zip, contains no PDFs, or any PDF fails to parse.

    Example:
        ```bash
        curl -F "file=@pozp-documents.zip" http://localhost:8000/calculate-tax
        ```
    """
    allowed_types = {"application/zip", "application/x-zip-compressed"}
    filename = file.filename or ""
    if file.content_type not in allowed_types and not filename.lower().endswith(".zip"):
        raise HTTPException(status_code=400, detail="File must be a ZIP archive.")

    raw = await file.read()

    try:
        with zipfile.ZipFile(BytesIO(raw)) as zip_file:
            pdf_entries = [
                name
                for name in zip_file.namelist()
                if name.lower().endswith(".pdf")
                and not name.startswith("__MACOSX/")
                and not name.startswith(".")
            ]
            if not pdf_entries:
                raise HTTPException(
                    status_code=400,
                    detail="No PDF files found in the uploaded zip archive.",
                )

            confirmations: list[ConfirmationOfATaxableIncome] = []
            for name in pdf_entries:
                pdf_bytes = zip_file.read(name)
                try:
                    confirmation = pdf_service.extract_confirmation_of_tax_income(
                        pdf_bytes
                    )
                except Exception as exc:
                    raise HTTPException(
                        status_code=400,
                        detail=f"Failed to parse '{name}'. Ensure it is a valid PDF.",
                    ) from exc
                confirmations.append(confirmation)
    except zipfile.BadZipFile as exc:
        raise HTTPException(status_code=400, detail="Invalid ZIP archive.") from exc

    return tax_service.calculate(confirmations)
