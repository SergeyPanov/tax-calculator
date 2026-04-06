from decimal import Decimal, ROUND_FLOOR, ROUND_HALF_UP

from backend.config import get_tax_annual_threshold_czk
from backend.models.confirmation_of_a_taxable_income import ConfirmationOfATaxableIncome
from backend.models.tax_result import TaxResult

_RATE_LOW = Decimal("0.15")
_RATE_HIGH = Decimal("0.23")
_SLEVA_NA_POPLATNIKA = Decimal("30840")
_ROUNDING_UNIT = Decimal("100")
_MONEY_QUANTIZE_UNIT = Decimal("0.01")
_MONEY_ROUNDING_MODE = ROUND_HALF_UP


def _d(value: Decimal | None) -> Decimal:
    """Return the value or zero when None."""
    return value if value is not None else Decimal(0)


def _money(value: Decimal) -> Decimal:
    """Normalize monetary values to 0.01 CZK precision."""
    return value.quantize(_MONEY_QUANTIZE_UNIT, rounding=_MONEY_ROUNDING_MODE)


class TaxCalculationService:

    def calculate(self, confirmations: list[ConfirmationOfATaxableIncome]) -> TaxResult:
        """Calculate annual income tax from one or more Potvrzení o zdanitelných příjmech.

        Implements Czech personal income tax (DPFO) calculation following DAP
        (Daňové přiznání) rules:
        - Rounds tax base down to nearest 100 CZK (DAP ř. 56)
        - Applies progressive rates: 15% up to ANNUAL_THRESHOLD_CZK and 23% above
          and rounds down once at the final tax amount (DAP ř. 57)
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

        aggregated_tax_base = _money(
            sum((_d(c.tax_base) for c in confirmations), Decimal(0))
        )
        aggregated_employment_income = _money(
            sum(
                (
                    _d(c.incomes_paid_till_january_31) + _d(c.additional_payments)
                    for c in confirmations
                ),
                Decimal(0),
            )
        )
        aggregated_advances = _money(
            sum(
                (_d(c.total_tax_advance) for c in confirmations),
                Decimal(0),
            )
        )
        rounded_tax_base = (aggregated_tax_base / _ROUNDING_UNIT).to_integral_value(
            rounding=ROUND_FLOOR
        ) * _ROUNDING_UNIT

        # Progressive tax: 15 % up to threshold, 23 % on the excess.
        # Bracket components are quantized to haléř precision (0.01 CZK),
        # then the combined tax is quantized to 0.01 CZK and floored once
        # at the end to whole CZK.
        income = aggregated_tax_base
        annual_threshold = get_tax_annual_threshold_czk()
        if income <= annual_threshold:
            tax_at_15 = _money(income * _RATE_LOW)
            tax_at_23 = _money(Decimal(0))
        else:
            tax_at_15 = _money(annual_threshold * _RATE_LOW)
            excess = income - annual_threshold
            tax_at_23 = _money(excess * _RATE_HIGH)

        unrounded_total_tax = _money(tax_at_15 + tax_at_23)
        total_tax = unrounded_total_tax.to_integral_value(rounding=ROUND_FLOOR)
        total_tax_credits = _money(_SLEVA_NA_POPLATNIKA)
        tax_after_credits = _money(max(Decimal(0), total_tax - total_tax_credits))
        overpayment_or_underpayment = _money(tax_after_credits - aggregated_advances)

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
