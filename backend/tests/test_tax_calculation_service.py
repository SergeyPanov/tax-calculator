from decimal import Decimal

import pytest

from backend.models.confirmation_of_a_taxable_income import ConfirmationOfATaxableIncome
from backend.services.tax_calculation_service import TaxCalculationService


def _make_confirmation(
    tax_base: Decimal | None = None,
    total_tax_advance: Decimal | None = None,
    incomes_paid_till_january_31: Decimal | None = None,
    additional_payments: Decimal | None = None,
) -> ConfirmationOfATaxableIncome:
    return ConfirmationOfATaxableIncome(
        total_accounted_incomes=None,
        incomes_paid_till_january_31=incomes_paid_till_january_31,
        accounted_in_months=None,
        additional_payments=additional_payments,
        tax_base=tax_base,
        tax_advance_from_row_2=None,
        tax_advance_from_row_4=None,
        total_tax_advance=total_tax_advance,
        monthly_tax_bonuses=None,
    )


class TestTaxCalculationService:
    def setup_method(self) -> None:
        self.service = TaxCalculationService()

    def test_below_threshold_15_pct_only(self) -> None:
        """Income entirely within the 15 % bracket."""
        c = _make_confirmation(
            tax_base=Decimal("1000000"),
            total_tax_advance=Decimal("150000"),
        )
        result = self.service.calculate([c])

        assert result.aggregated_tax_base == Decimal("1000000")
        assert result.rounded_tax_base == Decimal("1000000")
        assert result.tax_at_15_pct == Decimal("150000")
        assert result.tax_at_23_pct == Decimal("0")
        assert result.income_tax == Decimal("150000")
        assert result.total_tax_credits == Decimal("30840")
        assert result.tax_after_credits == Decimal("119160")
        assert result.overpayment_or_underpayment == Decimal("-30840")

    def test_above_threshold_progressive(self) -> None:
        """Income exceeds the 1,762,812 threshold — both brackets apply."""
        c = _make_confirmation(
            tax_base=Decimal("2000000"),
            total_tax_advance=Decimal("300000"),
        )
        result = self.service.calculate([c])

        # 15 % on 1,762,812 = 264,421.80 → floor → 264,421
        assert result.tax_at_15_pct == Decimal("264421")
        # 23 % on 237,188 = 54,553.24 → floor → 54,553
        assert result.tax_at_23_pct == Decimal("54553")
        assert result.income_tax == Decimal("318974")
        assert result.total_tax_credits == Decimal("30840")
        assert result.tax_after_credits == Decimal("288134")
        # overpayment: 288,134 − 300,000 = -11,866
        assert result.overpayment_or_underpayment == Decimal("-11866")

    def test_multiple_confirmations_aggregated(self) -> None:
        """Aggregates tax base and advances across two employers."""
        c1 = _make_confirmation(
            tax_base=Decimal("900000"),
            total_tax_advance=Decimal("135000"),
        )
        c2 = _make_confirmation(
            tax_base=Decimal("900000"),
            total_tax_advance=Decimal("135000"),
        )
        result = self.service.calculate([c1, c2])

        assert result.aggregated_tax_base == Decimal("1800000")
        assert result.aggregated_advances_withheld == Decimal("270000")
        assert len(result.confirmations) == 2

        # 15 % bracket fully used, plus 23 % on 37,188
        assert result.tax_at_15_pct == Decimal("264421")
        assert result.tax_at_23_pct == Decimal("8553")
        assert result.income_tax == Decimal("272974")
        assert result.tax_after_credits == Decimal("242134")

    def test_none_fields_default_to_zero(self) -> None:
        """All None fields should be treated as zero, producing zero tax."""
        c = _make_confirmation()
        result = self.service.calculate([c])

        assert result.aggregated_tax_base == Decimal("0")
        assert result.aggregated_advances_withheld == Decimal("0")
        assert result.income_tax == Decimal("0")
        assert result.tax_after_credits == Decimal("0")
        assert result.overpayment_or_underpayment == Decimal("0")

    def test_empty_list_raises_error(self) -> None:
        """An empty confirmations list must raise ValueError."""
        with pytest.raises(ValueError, match="At least one confirmation"):
            self.service.calculate([])

    def test_overpayment_when_advances_exceed_tax(self) -> None:
        """When withheld advances exceed computed tax, the result is negative (refund)."""
        c = _make_confirmation(
            tax_base=Decimal("500000"),
            total_tax_advance=Decimal("100000"),
        )
        result = self.service.calculate([c])

        # 15 % of 500,000 = 75,000
        assert result.income_tax == Decimal("75000")
        assert result.tax_after_credits == Decimal("44160")
        # 44,160 − 100,000 = −55,840  (overpayment / refund)
        assert result.overpayment_or_underpayment == Decimal("-55840")
