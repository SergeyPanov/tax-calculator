from decimal import Decimal
import io

import pdfplumber

from models.confirmation_of_a_taxable_income import ConfirmationOfATaxableIncome


class PdfService:
    # Maps row number (as printed on the 2025 form) to the model field name
    ROW_FIELD_MAP: dict[int, str] = {
        2: "incomes_paid_till_january_31",
        3: "accounted_in_months",
        4: "additional_payments",
        5: "tax_base",
        6: "tax_advance_from_row_2",
        7: "tax_advance_from_row_4",
        8: "total_tax_advance",
        9: "monthly_tax_bonuses",
    }

    # Czech label fragment used to identify the row-1 header (which has no "1." prefix)
    _ROW_1_LABEL = "úhrn zúčtovaných příjmů"

    def extract_confirmation_of_tax_income(self, content: bytes) -> ConfirmationOfATaxableIncome:
        extracted: dict[str, Decimal | str | None] = {}

        with pdfplumber.open(io.BytesIO(content)) as pdf:
            for page in pdf.pages:
                tables = page.extract_tables()
                if tables:
                    extracted.update(self._extract_from_tables(tables))

        return ConfirmationOfATaxableIncome(**extracted)

    def _parse_row_number(self, cell: str) -> int | None:
        stripped = cell.strip().rstrip(".")
        if stripped.isdigit():
            return int(stripped)
        return None


    def _parse_value(self, raw: str | None) -> Decimal | None:
        if not raw:
            return None
        cleaned = raw.strip().replace("\xa0", "").replace(" ", "")
        if cleaned.isdigit():
            return Decimal(cleaned)
        else:
            return None

    def _extract_from_tables(self, tables: list[list[list[str | None]]]) -> dict[str, Decimal | str | None]:
        data: dict[str, Decimal | str | None] = {}
        for table in tables:
            for row in table:
                if not row:
                    continue

                # Row 1 has no "1." prefix — detect via Czech label text
                if not row[0] and len(row) > 1 and row[1]:
                    label = row[1].lower()
                    if self._ROW_1_LABEL in label:
                        value_cell = self._last_non_empty(row[2:])
                        data["total_accounted_incomes"] = self._parse_value(value_cell)
                    continue

                if not row[0]:
                    continue

                row_num = self._parse_row_number(row[0])
                if row_num is None:
                    continue
                field = self.ROW_FIELD_MAP.get(row_num)
                if not field:
                    continue

                value_cell = self._last_non_empty(row[1:])

                # Row 3 (accounted_in_months) is a text value, not a number
                if field == "accounted_in_months":
                    data[field] = value_cell.strip() if value_cell else None
                else:
                    data[field] = self._parse_value(value_cell)
        return data

    @staticmethod
    def _last_non_empty(cells: list[str | None]) -> str | None:
        for c in reversed(cells):
            if c and c.strip() and not c.strip().startswith("XXX"):
                return c
        return None


