from decimal import Decimal

from pydantic import BaseModel, Field


class ConfirmationOfATaxableIncome(BaseModel):
    """Certificate of the taxable incomes from dependent activity and office holder's
    emoluments, the withheld tax advances and tax advantage (MFin 5460 — 2025 layout)."""

    # 1. Úhrn zúčtovaných příjmů ze závislé činnosti
    total_accounted_incomes: Decimal | None = Field(
        None, description="Row 1 - Total accounted incomes from dependent activity"
    )

    # 2. Z ř. 1 příjmy vyplacené nebo obdržené do 31. ledna
    incomes_paid_till_january_31: Decimal | None = Field(
        None, description="Row 2 - Incomes from row 1 paid or received till 31 January"
    )

    # 3. Zúčtováno v měsících (číselné označení)
    accounted_in_months: str | None = Field(
        None, description="Row 3 - Accounted in the months (numerical indication, e.g. '01 02 03')"
    )

    # 4. Doplatky příjmů podle § 5 odst. 4 zákona
    additional_payments: Decimal | None = Field(
        None, description="Row 4 - Additional payments of the incomes (§ 5 subsection 4)"
    )

    # 5. Základ daně (ř. 2 + ř. 4)
    tax_base: Decimal | None = Field(
        None, description="Row 5 - Tax base (row 2 + row 4)"
    )

    # 6. Skutečně sražená záloha na daň z příjmů uvedených na ř. 2
    tax_advance_from_row_2: Decimal | None = Field(
        None, description="Row 6 - Tax advance actually withheld from incomes on row 2"
    )

    # 7. Skutečně sražená záloha na daň z příjmů uvedených na ř. 4
    tax_advance_from_row_4: Decimal | None = Field(
        None, description="Row 7 - Tax advance actually withheld from incomes on row 4"
    )

    # 8. Záloha na daň z příjmů celkem (ř. 6 + ř. 7)
    total_tax_advance: Decimal | None = Field(
        None, description="Row 8 - Total tax advance (row 6 + row 7)"
    )

    # 9. Úhrn vyplacených měsíčních daňových bonusů
    monthly_tax_bonuses: Decimal | None = Field(
        None, description="Row 9 - Total monthly tax bonuses paid out"
    )
