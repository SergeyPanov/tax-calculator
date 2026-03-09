import io
from decimal import Decimal, InvalidOperation

import pdfplumber
from fastapi import APIRouter, UploadFile, File, HTTPException

from models.confirmation_of_a_taxable_income import ConfirmationOfATaxableIncome

router = APIRouter()

# Maps row number to the model field name
ROW_FIELD_MAP: dict[int, str] = {
    1: "total_accounted_incomes",
    2: "incomes_paid_till_january_31",
    3: "accounted_in_months",
    4: "additional_payments_2005_2007",
    5: "additional_payments_2008_2011",
    6: "total_compulsory_premium_insurance",
    7: "total_employer_premium_insurance",
    8: "tax_base",
    9: "tax_advance_from_row_2",
    10: "tax_advance_from_row_4",
}


def _parse_row_number(cell: str) -> int | None:
    stripped = cell.strip().rstrip(".")
    if stripped.isdigit():
        return int(stripped)
    return None


def _parse_value(raw: str | None, field: str) -> Decimal | str | None:
    if not raw:
        return None
    cleaned = raw.strip().replace("\xa0", "").replace(" ", "")
    if field == "accounted_in_months":
        return cleaned or None
    cleaned = cleaned.replace(",", ".")
    try:
        return Decimal(cleaned)
    except InvalidOperation:
        return None


def _extract_from_tables(tables: list[list[list[str | None]]]) -> dict[str, Decimal | str | None]:
    data: dict[str, Decimal | str | None] = {}
    for table in tables:
        for row in table:
            if not row or not row[0]:
                continue
            row_num = _parse_row_number(row[0])
            if row_num is None:
                continue
            field = ROW_FIELD_MAP.get(row_num)
            if not field:
                continue
            # Value is typically in the last non-empty cell
            value_cell = next((c for c in reversed(row[1:]) if c and c.strip()), None)
            data[field] = _parse_value(value_cell, field)
    return data


@router.post("/upload-pdf")
async def upload_pdf(file: UploadFile = File(...)) -> ConfirmationOfATaxableIncome:
    if file.content_type != "application/pdf":
        raise HTTPException(status_code=400, detail="File must be a PDF")

    contents = await file.read()
    extracted: dict[str, Decimal | str | None] = {}

    # Try pdfplumber first (works on text-based / digitally filled PDFs)
    with pdfplumber.open(io.BytesIO(contents)) as pdf:
        for page in pdf.pages:
            tables = page.extract_tables()
            if tables:
                extracted.update(_extract_from_tables(tables))

    return ConfirmationOfATaxableIncome(**extracted)
