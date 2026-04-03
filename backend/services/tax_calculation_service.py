from decimal import Decimal, ROUND_FLOOR

from backend.models.confirmation_of_a_taxable_income import ConfirmationOfATaxableIncome
from backend.models.tax_result import TaxResult

# 2026 annual threshold: 36× average monthly wage (48,967 CZK × 36 = 1,762,812)
_BRACKET_THRESHOLD = Decimal("1762812")
_RATE_LOW = Decimal("0.15")
_RATE_HIGH = Decimal("0.23")
_SLEVA_NA_POPLATNIKA = Decimal("30840")
_ROUNDING_UNIT = Decimal("100")


def _d(value: Decimal | None) -> Decimal:
    """Return the value or zero when None."""
    return value if value is not None else Decimal(0)


class TaxCalculationService:

    def calculate(self, confirmations: list[ConfirmationOfATaxableIncome]) -> TaxResult:
        """Calculate annual income tax from one or more Potvrzení o zdanitelných příjmech.

        Implements Czech personal income tax (DPFO) calculation following DAP
        (Daňové přiznání) rules:
        - Rounds tax base down to nearest 100 CZK (DAP ř. 56)
        - Applies progressive rates: 15% on first CZK 1,762,812, 23% above (DAP ř. 57)
        - Applies sleva na poplatníka (CZK 30,840) automatically (DAP ř. 70)
        - Computes tax after credits with MAX(0, tax - credits) (DAP ř. 71)
        - Calculates overpayment/underpayment vs. withheld advances (DAP ř. 84)

        Args:
            confirmations: List of parsed MFin 5460 forms. Must contain at least one.

        Returns:
            TaxResult with aggregated values and DAP-aligned fields.

        Raises:
            ValueError: If confirmations list is empty.

        Example:
            >>> service = TaxCalculationService()
            >>> confirmation = ConfirmationOfATaxableIncome(
            ...     tax_base=Decimal("1704925"),
            ...     total_tax_advance=Decimal("282298")
            ... )
            >>> result = service.calculate([confirmation])
            >>> result.rounded_tax_base
            Decimal('1704900')
            >>> result.income_tax
            Decimal('255735')
            >>> result.tax_after_credits
            Decimal('224895')
            >>> result.overpayment_or_underpayment
            Decimal('-57403')
        """
        if not confirmations:
            raise ValueError("At least one confirmation is required")

        aggregated_tax_base = sum((_d(c.tax_base) for c in confirmations), Decimal(0))
        aggregated_employment_income = sum(
            (
                _d(c.incomes_paid_till_january_31) + _d(c.additional_payments)
                for c in confirmations
            ),
            Decimal(0),
        )
        aggregated_advances = sum(
            (_d(c.total_tax_advance) for c in confirmations),
            Decimal(0),
        )
        rounded_tax_base = (aggregated_tax_base / _ROUNDING_UNIT).to_integral_value(
            rounding=ROUND_FLOOR
        ) * _ROUNDING_UNIT

        # Progressive tax: 15 % up to threshold, 23 % on the excess
        if rounded_tax_base <= _BRACKET_THRESHOLD:
            tax_at_15 = (rounded_tax_base * _RATE_LOW).to_integral_value(
                rounding=ROUND_FLOOR
            )
            tax_at_23 = Decimal(0)
        else:
            tax_at_15 = (_BRACKET_THRESHOLD * _RATE_LOW).to_integral_value(
                rounding=ROUND_FLOOR
            )
            excess = rounded_tax_base - _BRACKET_THRESHOLD
            tax_at_23 = (excess * _RATE_HIGH).to_integral_value(rounding=ROUND_FLOOR)

        total_tax = tax_at_15 + tax_at_23
        total_tax_credits = _SLEVA_NA_POPLATNIKA
        tax_after_credits = max(Decimal(0), total_tax - total_tax_credits)
        overpayment_or_underpayment = tax_after_credits - aggregated_advances

        return TaxResult(
            confirmations=confirmations,
            aggregated_tax_base=aggregated_tax_base,
            aggregated_advances_withheld=aggregated_advances,
            total_employment_income=aggregated_employment_income,
            partial_tax_base=aggregated_tax_base,
            rounded_tax_base=rounded_tax_base,
            income_tax=total_tax,
            total_tax_credits=total_tax_credits,
            tax_after_credits=tax_after_credits,
            advances_withheld=aggregated_advances,
            tax_at_15_pct=tax_at_15,
            tax_at_23_pct=tax_at_23,
            total_tax=total_tax,
            overpayment_or_underpayment=overpayment_or_underpayment,
        )
