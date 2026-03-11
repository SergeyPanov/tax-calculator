from decimal import Decimal

from pydantic import BaseModel, Field


class ConfirmationOfATaxableIncome(BaseModel):
    """Certificate of the taxable incomes from dependent activity and office holder's
    emoluments, the withheld tax advances and tax advantage (MFin 5460)."""

    # 1. Total accounted incomes from dependent activity and office holder's emoluments
    total_accounted_incomes: Decimal | None = Field(
        None, description="Row 1 - Total accounted incomes from dependent activity and office holder's emoluments"
    )

    # 2. Incomes from row 1 paid or received till 31 January (§ 5 subsection 4 of the Act)
    incomes_paid_till_january_31: Decimal | None = Field(
        None, description="Row 2 - Incomes from row 1 paid or received till 31 January"
    )

    # 3. Accounted in the months (numerical indication)
    accounted_in_months: Decimal | None = Field(
        None, description="Row 3 - Accounted in the months (numerical indication)"
    )

    # 4. Additional payments of the incomes pursuant to § 5 subsection 4 of the Act
    #    accounted in the taxable periods 2005 to 2007
    additional_payments_2005_2007: Decimal | None = Field(
        None, description="Row 4 - Additional payments of the incomes (taxable periods 2005–2007)"
    )

    # 5. Additional payments of the incomes pursuant to § 5 subsection 4 of the Act
    #    accounted in the taxable periods 2008–2011
    additional_payments_2008_2011: Decimal | None = Field(
        None, description="Row 5 - Additional payments of the incomes (taxable periods 2008–2011)"
    )

    # 6. Total compulsory premium insurance from the incomes stated on row 2
    #    (§ 6 subsection 13 of the Act)
    total_compulsory_premium_insurance: Decimal | None = Field(
        None, description="Row 6 - Total compulsory premium insurance from the incomes stated on row 2"
    )

    # 7. Total premium insurance, which was an employer obliged to pay from
    #    the incomes stated on row 5
    total_employer_premium_insurance: Decimal | None = Field(
        None, description="Row 7 - Total premium insurance an employer was obliged to pay from incomes on row 5"
    )

    # 8. Tax base (row 2 + row 4 + row 5 + row 6 + row 7)
    tax_base: Decimal | None = Field(
        None, description="Row 8 - Tax base (row 2 + row 4 + row 5 + row 6 + row 7)"
    )

    # 9. Tax advance actually withheld from incomes stated on row 2
    tax_advance_from_row_2: Decimal | None = Field(
        None, description="Row 9 - Tax advance actually withheld from incomes stated on row 2"
    )

    # 10. Tax advance actually withheld from incomes stated on row 4
    tax_advance_from_row_4: Decimal | None = Field(
        None, description="Row 10 - Tax advance actually withheld from incomes stated on row 4"
    )
