
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
