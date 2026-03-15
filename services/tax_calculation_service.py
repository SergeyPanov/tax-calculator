from decimal import Decimal, ROUND_FLOOR

from models.confirmation_of_a_taxable_income import ConfirmationOfATaxableIncome
from models.tax_result import TaxResult

# 2026 annual threshold: 36× average monthly wage (48,967 CZK × 36 = 1,762,812)
_BRACKET_THRESHOLD = Decimal("1762812")
_RATE_LOW = Decimal("0.15")
_RATE_HIGH = Decimal("0.23")


def _d(value: Decimal | None) -> Decimal:
    """Return the value or zero when None."""
    return value if value is not None else Decimal(0)


class TaxCalculationService:

    def calculate(
        self, confirmations: list[ConfirmationOfATaxableIncome]
    ) -> TaxResult:
        if not confirmations:
            raise ValueError("At least one confirmation is required")

        aggregated_tax_base = sum(
            (_d(c.tax_base) for c in confirmations), Decimal(0)
        )
        aggregated_advances = sum(
            (_d(c.total_tax_advance)
             for c in confirmations),
            Decimal(0),
        )

        # Progressive tax: 15 % up to threshold, 23 % on the excess
        if aggregated_tax_base <= _BRACKET_THRESHOLD:
            tax_at_15 = (aggregated_tax_base * _RATE_LOW).to_integral_value(
                rounding=ROUND_FLOOR
            )
            tax_at_23 = Decimal(0)
        else:
            tax_at_15 = (_BRACKET_THRESHOLD * _RATE_LOW).to_integral_value(
                rounding=ROUND_FLOOR
            )
            excess = aggregated_tax_base - _BRACKET_THRESHOLD
            tax_at_23 = (excess * _RATE_HIGH).to_integral_value(
                rounding=ROUND_FLOOR
            )

        total_tax = tax_at_15 + tax_at_23
        overpayment_or_underpayment = total_tax - aggregated_advances

        return TaxResult(
            confirmations=confirmations,
            aggregated_tax_base=aggregated_tax_base,
            aggregated_advances_withheld=aggregated_advances,
            tax_at_15_pct=tax_at_15,
            tax_at_23_pct=tax_at_23,
            total_tax=total_tax,
            overpayment_or_underpayment=overpayment_or_underpayment,
        )
