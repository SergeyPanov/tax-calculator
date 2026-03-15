from decimal import Decimal

import pytest

from models.confirmation_of_a_taxable_income import ConfirmationOfATaxableIncome
from services.tax_calculation_service import TaxCalculationService


def _make_confirmation(
    tax_base: Decimal | None = None,
    total_tax_advance: Decimal | None = None,
) -> ConfirmationOfATaxableIncome:
    return ConfirmationOfATaxableIncome(
        tax_base=tax_base,
        total_tax_advance=total_tax_advance,
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
        assert result.tax_at_15_pct == Decimal("150000")
        assert result.tax_at_23_pct == Decimal("0")
        assert result.total_tax == Decimal("150000")
        assert result.overpayment_or_underpayment == Decimal("0")

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
        assert result.total_tax == Decimal("318974")
        # underpayment: 318,974 − 300,000 = 18,974
        assert result.overpayment_or_underpayment == Decimal("18974")

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
        excess_tax = (Decimal("37188") * Decimal("0.23")).to_integral_value()
        assert result.tax_at_23_pct == Decimal("8553")

    def test_none_fields_default_to_zero(self) -> None:
        """All None fields should be treated as zero, producing zero tax."""
        c = _make_confirmation()
        result = self.service.calculate([c])

        assert result.aggregated_tax_base == Decimal("0")
        assert result.aggregated_advances_withheld == Decimal("0")
        assert result.total_tax == Decimal("0")
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
        assert result.total_tax == Decimal("75000")
        # 75,000 − 100,000 = −25,000  (overpayment / refund)
        assert result.overpayment_or_underpayment == Decimal("-25000")
