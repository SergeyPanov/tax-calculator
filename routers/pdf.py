
from fastapi import APIRouter, Depends, UploadFile, File, HTTPException

from models.confirmation_of_a_taxable_income import ConfirmationOfATaxableIncome
from models.tax_result import TaxResult
from services.pdf_service import PdfService
from services.tax_calculation_service import TaxCalculationService

router = APIRouter()

def get_pdf_service() -> PdfService:
    return PdfService()

def get_tax_calculation_service() -> TaxCalculationService:
    return TaxCalculationService()

@router.post("/upload-pdf")
async def upload_pdf(file: UploadFile = File(...), pdf_service: PdfService = Depends(get_pdf_service) ) -> ConfirmationOfATaxableIncome:
    """Extract fields from a Potvrzení o zdanitelných příjmech (MFin 5460) PDF.

    Parses the PDF table and returns structured data (tax base, withheld advances,
    bonuses) without performing tax calculation.

    Args:
        file: Uploaded PDF file (must be application/pdf).
        pdf_service: PDF parsing service (dependency-injected).

    Returns:
        ConfirmationOfATaxableIncome with extracted fields.

    Raises:
        HTTPException(400): If file is not a PDF or parsing fails.

    Example:
        ```bash
        curl -F "file=@MSFT-POZP-2025.pdf" http://localhost:8000/upload-pdf
        ```

        Response:
        ```json
        {
          "incomes_paid_till_january_31": "1704925",
          "tax_base": "1704925",
          "total_tax_advance": "282298"
        }
        ```
    """
    if file.content_type != "application/pdf":
        raise HTTPException(status_code=400, detail="File must be a PDF")

    content = await file.read()

    try:
        return pdf_service.extract_confirmation_of_tax_income(content)
    except Exception as exc:
        # Convert PDF parsing errors into a client error instead of a 500.
        raise HTTPException(
            status_code=400,
            detail="Failed to parse PDF file. Ensure the file is a valid, non-corrupted PDF.",
        ) from exc


@router.post("/calculate-tax")
async def calculate_tax(
    file: UploadFile = File(...),
    pdf_service: PdfService = Depends(get_pdf_service),
    tax_service: TaxCalculationService = Depends(get_tax_calculation_service),
) -> TaxResult:
    """Parse a Potvrzení PDF and calculate annual DPFO income tax (DAP-compliant).

    Extracts tax base and withheld advances from the PDF, then computes:
    - Tax base rounded to nearest 100 CZK (DAP ř. 56)
    - Progressive income tax: 15% on first CZK 1,762,812, 23% above (DAP ř. 57)
    - Sleva na poplatníka (CZK 30,840) applied automatically (DAP ř. 70)
    - Tax after credits (DAP ř. 71)
    - Overpayment/underpayment vs. withheld advances (DAP ř. 84)

    Args:
        file: Uploaded PDF file (must be application/pdf).
        pdf_service: PDF parsing service (dependency-injected).
        tax_service: Tax calculation service (dependency-injected).

    Returns:
        TaxResult with DAP-aligned fields and calculated tax.

    Raises:
        HTTPException(400): If file is not a PDF or parsing fails.

    Example:
        ```bash
        curl -F "file=@MSFT-POZP-2025.pdf" http://localhost:8000/calculate-tax
        ```

        Response (CZK 1,704,925 tax base, CZK 282,298 withheld):
        ```json
        {
          "rounded_tax_base": "1704900",
          "income_tax": "255735",
          "tax_after_credits": "224895",
          "overpayment_or_underpayment": "-57403"
        }
        ```

        The negative overpayment (-57,403 CZK) means a refund (přeplatek).
    """
    if file.content_type != "application/pdf":
        raise HTTPException(
            status_code=400,
            detail=f"File '{file.filename}' is not a PDF",
        )

    content = await file.read()

    try:
        confirmation = pdf_service.extract_confirmation_of_tax_income(content)
    except Exception as exc:
        raise HTTPException(
            status_code=400,
            detail=f"Failed to parse '{file.filename}'. Ensure it is a valid PDF.",
        ) from exc

    return tax_service.calculate([confirmation])
