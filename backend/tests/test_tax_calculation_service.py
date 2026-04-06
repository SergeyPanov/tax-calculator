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
    @pytest.fixture(autouse=True)
    def _set_required_threshold_env(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setenv("ANNUAL_THRESHOLD_CZK", "1676052")

    def setup_method(self) -> None:
        self.service = TaxCalculationService()

    def test_below_threshold_15_pct_only(self) -> None:
        """Income entirely within the 15 % bracket."""
        c = _make_confirmation(
            tax_base=Decimal("1000000"),
            total_tax_advance=Decimal("150000"),
        )
        result = self.service.calculate([c])

        assert result.aggregated_tax_base == Decimal("1000000.00")
        assert result.rounded_tax_base == Decimal("1000000")
        assert result.tax_at_15_pct == Decimal("150000.00")
        assert result.tax_at_23_pct == Decimal("0.00")
        assert result.tax_at_15_pct.as_tuple().exponent == -2
        assert result.tax_at_23_pct.as_tuple().exponent == -2
        assert result.income_tax == Decimal("150000")
        assert result.aggregated_tax_base.as_tuple().exponent == -2
        assert result.total_tax_credits.as_tuple().exponent == -2
        assert result.tax_after_credits.as_tuple().exponent == -2
        assert result.overpayment_or_underpayment.as_tuple().exponent == -2
        assert result.total_tax_credits == Decimal("30840.00")
        assert result.tax_after_credits == Decimal("119160.00")
        assert result.overpayment_or_underpayment == Decimal("-30840.00")

    def test_above_threshold_progressive(self) -> None:
        """Income exceeds threshold and preserves current split/tax result."""
        c = _make_confirmation(
            tax_base=Decimal("2000000"),
            total_tax_advance=Decimal("300000"),
        )
        result = self.service.calculate([c])

        # Threshold 1,676,052 => 15 % + 23 % split unchanged.
        assert result.tax_at_15_pct == Decimal("251407.80")
        assert result.tax_at_23_pct == Decimal("74508.04")
        assert result.income_tax == Decimal("325915")
        assert result.total_tax_credits == Decimal("30840.00")
        assert result.tax_after_credits == Decimal("295075.00")
        # overpayment: 295,075 − 300,000 = -4,925
        assert result.overpayment_or_underpayment == Decimal("-4925.00")

    def test_threshold_1676052_for_2000000_income_is_325915(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """With threshold 1,676,052, 2,000,000 CZK tax floors to 325,915 CZK."""
        monkeypatch.setenv("ANNUAL_THRESHOLD_CZK", "1676052")
        c = _make_confirmation(
            tax_base=Decimal("2000000"),
            total_tax_advance=Decimal("0"),
        )

        result = self.service.calculate([c])

        assert result.tax_at_15_pct == Decimal("251407.80")
        assert result.tax_at_23_pct == Decimal("74508.04")
        assert result.tax_at_15_pct + result.tax_at_23_pct == Decimal("325915.84")
        assert result.income_tax == Decimal("325915")

    @pytest.mark.parametrize(
        ("income", "expected_tax_15", "expected_tax_23", "expected_tax"),
        [
            (
                Decimal("1676051"),
                Decimal("251407.65"),
                Decimal("0.00"),
                Decimal("251407"),
            ),
            (
                Decimal("1676052"),
                Decimal("251407.80"),
                Decimal("0.00"),
                Decimal("251407"),
            ),
            (
                Decimal("1676053"),
                Decimal("251407.80"),
                Decimal("0.23"),
                Decimal("251408"),
            ),
            (
                Decimal("1676057"),
                Decimal("251407.80"),
                Decimal("1.15"),
                Decimal("251408"),
            ),
            (
                Decimal("1676058"),
                Decimal("251407.80"),
                Decimal("1.38"),
                Decimal("251409"),
            ),
        ],
    )
    def test_income_tax_formula_threshold_edges(
        self,
        income: Decimal,
        expected_tax_15: Decimal,
        expected_tax_23: Decimal,
        expected_tax: Decimal,
    ) -> None:
        """Threshold-edge values keep 0.01 CZK brackets and floor once at final tax."""
        c = _make_confirmation(
            tax_base=income,
            total_tax_advance=Decimal("0"),
        )

        result = self.service.calculate([c])

        assert result.tax_at_15_pct == expected_tax_15
        assert result.tax_at_23_pct == expected_tax_23
        assert result.tax_at_15_pct.as_tuple().exponent == -2
        assert result.tax_at_23_pct.as_tuple().exponent == -2
        assert result.income_tax == expected_tax

    def test_just_above_threshold_pre_floor_sum_then_single_floor(self) -> None:
        """Bracket parts are summed at haléř precision; floor is applied once."""
        c = _make_confirmation(
            tax_base=Decimal("1676054"),
            total_tax_advance=Decimal("0"),
        )

        result = self.service.calculate([c])

        assert result.tax_at_15_pct == Decimal("251407.80")
        assert result.tax_at_23_pct == Decimal("0.46")
        assert result.tax_at_15_pct + result.tax_at_23_pct == Decimal("251408.26")
        assert result.income_tax == Decimal("251408")

    def test_uses_env_threshold_for_progressive_split(
        self,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        """Progressive split uses ANNUAL_THRESHOLD_CZK from environment."""
        monkeypatch.setenv("ANNUAL_THRESHOLD_CZK", "1000000")
        c = _make_confirmation(
            tax_base=Decimal("1200000"),
            total_tax_advance=Decimal("0"),
        )

        result = self.service.calculate([c])

        assert result.tax_at_15_pct == Decimal("150000.00")
        assert result.tax_at_23_pct == Decimal("46000.00")
        assert result.income_tax == Decimal("196000")

    def test_fractional_income_uses_decimal_half_up_quantization(self) -> None:
        """Fractional income rounds bracket to 0.01 with HALF_UP, without float math."""
        c = _make_confirmation(
            tax_base=Decimal("1000000.10"),
            total_tax_advance=Decimal("0"),
        )

        result = self.service.calculate([c])

        assert result.tax_at_15_pct == Decimal("150000.02")
        assert result.tax_at_23_pct == Decimal("0.00")
        assert result.tax_at_15_pct.as_tuple().exponent == -2
        assert result.income_tax == Decimal("150000")

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

        assert result.aggregated_tax_base == Decimal("1800000.00")
        assert result.aggregated_advances_withheld == Decimal("270000.00")
        assert len(result.confirmations) == 2

        # 15 % bracket fully used, plus 23 % on 123,948; final tax floored once
        assert result.tax_at_15_pct == Decimal("251407.80")
        assert result.tax_at_23_pct == Decimal("28508.04")
        assert result.income_tax == Decimal("279915")
        assert result.tax_after_credits == Decimal("249075.00")

    def test_none_fields_default_to_zero(self) -> None:
        """All None fields should be treated as zero, producing zero tax."""
        c = _make_confirmation()
        result = self.service.calculate([c])

        assert result.aggregated_tax_base == Decimal("0.00")
        assert result.aggregated_advances_withheld == Decimal("0.00")
        assert result.income_tax == Decimal("0")
        assert result.tax_after_credits == Decimal("0.00")
        assert result.overpayment_or_underpayment == Decimal("0.00")
        assert result.aggregated_tax_base.as_tuple().exponent == -2
        assert result.aggregated_advances_withheld.as_tuple().exponent == -2

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
        assert result.tax_after_credits == Decimal("44160.00")
        # 44,160 − 100,000 = −55,840  (overpayment / refund)
        assert result.overpayment_or_underpayment == Decimal("-55840.00")
