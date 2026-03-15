from decimal import Decimal

from pydantic import BaseModel, Field

from models.confirmation_of_a_taxable_income import ConfirmationOfATaxableIncome


class TaxResult(BaseModel):
    """Aggregated tax calculation result from multiple Potvrzení o zdanitelných příjmech."""

    confirmations: list[ConfirmationOfATaxableIncome] = Field(
        description="Parsed data from each uploaded confirmation"
    )
    aggregated_tax_base: Decimal = Field(
        description="Sum of tax_base (row 8) across all confirmations"
    )
    aggregated_advances_withheld: Decimal = Field(
        description="Sum of tax advances withheld (row 9 + row 10) across all confirmations"
    )
    tax_at_15_pct: Decimal = Field(
        description="Tax computed at 15% on the first CZK 1,762,812 of the aggregated tax base"
    )
    tax_at_23_pct: Decimal = Field(
        description="Tax computed at 23% on the aggregated tax base exceeding CZK 1,762,812"
    )
    total_tax: Decimal = Field(
        description="Total annual income tax (tax_at_15_pct + tax_at_23_pct), rounded down to whole CZK"
    )
    overpayment_or_underpayment: Decimal = Field(
        description="total_tax - aggregated_advances_withheld; negative means overpayment (refund)"
    )
