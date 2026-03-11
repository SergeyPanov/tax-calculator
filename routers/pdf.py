
from fastapi import APIRouter, Depends, UploadFile, File, HTTPException

from models.confirmation_of_a_taxable_income import ConfirmationOfATaxableIncome
from services.pdf_service import PdfService

router = APIRouter()

def get_pdf_service() -> PdfService:
    return PdfService()

@router.post("/upload-pdf")
async def upload_pdf(file: UploadFile = File(...), pdf_service: PdfService = Depends(get_pdf_service) ) -> ConfirmationOfATaxableIncome:
    if file.content_type != "application/pdf":
        raise HTTPException(status_code=400, detail="File must be a PDF")

    content = await file.read()
    
    return pdf_service.extract_confirmation_of_tax_income(content)
