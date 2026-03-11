from decimal import Decimal
import io

import pdfplumber

from models.confirmation_of_a_taxable_income import ConfirmationOfATaxableIncome


class PdfService:
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
    
    def extract_confirmation_of_tax_income(self, content: bytes) -> ConfirmationOfATaxableIncome:
        extracted: dict[str, Decimal | None] = {}

        # Try pdfplumber first (works on text-based / digitally filled PDFs)
        with pdfplumber.open(io.BytesIO(content)) as pdf:
            for page in pdf.pages:
                tables = page.extract_tables()
                if tables:
                    extracted = self._extract_from_tables(tables)

        return ConfirmationOfATaxableIncome(**extracted)

    def _parse_row_number(self, cell: str) -> int | None:
        stripped = cell.strip().rstrip(".")
        if stripped.isdigit():
            return int(stripped)
        return None


    def _parse_value(self, raw: str | None, field: str) -> Decimal | None:
        if not raw:
            return None
        cleaned = raw.strip().replace("\xa0", "").replace(" ", "")
        if cleaned.isdigit():
            return Decimal(cleaned)
        else:
            return None

    def _extract_from_tables(self, tables: list[list[list[str | None]]]) -> dict[str, Decimal  | None]:
        data: dict[str, Decimal | None] = {}
        for table in tables:
            for row in table:
                if not row or not row[0]:
                    continue
                row_num = self._parse_row_number(row[0])
                if row_num is None:
                    continue
                field = self.ROW_FIELD_MAP.get(row_num)
                if not field:
                    continue
                # Value is typically in the last non-empty cell
                value_cell = None
                for c in reversed(row[1:]):
                    if c and c.strip():
                        value_cell = c
                        break
                data[field] = self._parse_value(value_cell, field)
        return data


