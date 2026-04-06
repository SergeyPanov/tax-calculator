from decimal import Decimal

from pydantic import BaseModel, Field

from backend.models.confirmation_of_a_taxable_income import ConfirmationOfATaxableIncome


class TaxResult(BaseModel):
    """Aggregated tax calculation result from multiple Potvrzení o zdanitelných příjmech."""

    confirmations: list[ConfirmationOfATaxableIncome] = Field(
        description="Parsed data from each uploaded confirmation"
    )
    aggregated_tax_base: Decimal = Field(
        description="Sum of tax_base across all confirmations, normalized to 0.01 CZK (ROUND_HALF_UP)"
    )
    aggregated_advances_withheld: Decimal = Field(
        description="Sum of withheld tax advances across all confirmations, normalized to 0.01 CZK (ROUND_HALF_UP)"
    )
    total_employment_income: Decimal = Field(
        description=(
            "DAP row 31 total employment income (incomes_paid_till_january_31 + additional_payments), "
            "normalized to 0.01 CZK (ROUND_HALF_UP)"
        )
    )
    partial_tax_base: Decimal = Field(
        description="DAP row 36 partial tax base from dependent activity, normalized to 0.01 CZK (ROUND_HALF_UP)"
    )
    rounded_tax_base: Decimal = Field(
        description="DAP row 56 tax base rounded down to the nearest 100 CZK"
    )
    income_tax: Decimal = Field(
        description=(
            "DAP row 57 final income tax rounded down once to whole CZK from "
            "0.01-CZK quantized bracket components (tax_at_15_pct + tax_at_23_pct)"
        )
    )
    total_tax_credits: Decimal = Field(
        description="DAP row 70 sum of applied tax credits (slevy)"
    )
    tax_after_credits: Decimal = Field(
        description="DAP row 71 tax after credits (max of zero and income_tax - total_tax_credits), normalized to 0.01 CZK (ROUND_HALF_UP)"
    )
    advances_withheld: Decimal = Field(
        description="DAP row 84 total withheld advances (sražené zálohy), normalized to 0.01 CZK (ROUND_HALF_UP)"
    )
    tax_at_15_pct: Decimal = Field(
        description=(
            "15% component quantized to 0.01 CZK: 0.15 × min(aggregated_tax_base, ANNUAL_THRESHOLD_CZK) "
            "before final FLOOR rounding of total tax"
        )
    )
    tax_at_23_pct: Decimal = Field(
        description=(
            "23% component quantized to 0.01 CZK: 0.23 × max(aggregated_tax_base - ANNUAL_THRESHOLD_CZK, 0) "
            "before final FLOOR rounding of total tax"
        )
    )
    total_tax: Decimal = Field(
        description=(
            "Total annual income tax after 0.01-CZK quantization of bracket components "
            "and combined pre-floor total, then a single final ROUND_FLOOR to whole CZK; "
            "equivalent to income_tax"
        )
    )
    overpayment_or_underpayment: Decimal = Field(
        description="tax_after_credits - advances_withheld, normalized to 0.01 CZK (ROUND_HALF_UP); negative means overpayment (refund)"
    )
