---
applyTo: "**"
---

# Rules: Filling Daňové přiznání (DAP) from Potvrzení o zdanitelných příjmech (MFin 5460)

These rules define how to map fields from `ConfirmationOfATaxableIncome` (the parsed
"Potvrzení o zdanitelných příjmech", MFin 5460) to the correct lines of the Czech personal
income tax return (Přiznání k dani z příjmů fyzických osob).

---

## Field Mapping: MFin 5460 → DAP

| POZP field (model) | POZP row | Czech label on form | → DAP line | Czech DAP label |
|---|---|---|---|---|
| `incomes_paid_till_january_31` | ř. 2 | Příjmy vyplacené nebo obdržené do 31. ledna | **DAP ř. 31** | Úhrn příjmů od zaměstnavatele |
| `additional_payments` | ř. 4 | Doplatky příjmů podle § 5 odst. 4 | **DAP ř. 31** | Included in total with ř. 2 |
| `tax_base` | ř. 5 | Základ daně (ř. 2 + ř. 4) | **DAP ř. 36** | Dílčí základ daně ze závislé činnosti (§ 6) |
| `tax_advance_from_row_2` | ř. 6 | Sražená záloha z příjmů na ř. 2 | **DAP ř. 84** | Úhrn sražených záloh |
| `tax_advance_from_row_4` | ř. 7 | Sražená záloha z příjmů na ř. 4 | **DAP ř. 84** | Included in total with ř. 6 |
| `total_tax_advance` | ř. 8 | Záloha na daň celkem (ř. 6 + ř. 7) | **DAP ř. 84** | Úhrn sražených záloh (final value to use) |
| `monthly_tax_bonuses` | ř. 9 | Úhrn vyplacených měsíčních daňových bonusů | **DAP ř. 75** | Úhrn vyplacených měsíčních daňových bonusů |
| `accounted_in_months` | ř. 3 | Zúčtováno v měsících | Supporting info only — verify employment period |

---

## Calculation Rules

### Rule 1 — DAP ř. 31: Total employment income
```
DAP ř. 31 = SUM(incomes_paid_till_january_31 + additional_payments)
            across all POZP documents from all employers
```
Use `incomes_paid_till_january_31` (ř. 2) as the base income.
Add `additional_payments` (ř. 4) if non-zero.

### Rule 2 — DAP ř. 36: Partial tax base from dependent activity (§ 6)
```
DAP ř. 36 = SUM(tax_base) across all POZP documents
```
`tax_base` (ř. 5) on the POZP already equals ř. 2 + ř. 4, so summing directly is correct.
Copy ř. 36 to **DAP ř. 41** if no other income types exist.

### Rule 3 — DAP ř. 56: Tax base rounded
```
DAP ř. 56 = ROUND_DOWN(DAP ř. 45 − odečitatelné položky, to nearest 100 CZK)
```
DAP ř. 45 = total tax base (sum of all partial bases).

### Rule 4 — DAP ř. 57: Income tax (DPFO, § 16)
```
If DAP ř. 56 ≤ 1 762 812:
    DAP ř. 57 = FLOOR(DAP ř. 56 × 0.15)

If DAP ř. 56 > 1 762 812:
    DAP ř. 57 = FLOOR(1 762 812 × 0.15)
              + FLOOR((DAP ř. 56 − 1 762 812) × 0.23)
```
All amounts rounded down (`ROUND_FLOOR`) to whole CZK.

### Rule 5 — DAP ř. 71: Tax after credits (slevy na dani)
```
DAP ř. 71 = MAX(0, DAP ř. 60 − DAP ř. 70)
```
DAP ř. 70 = sum of all applicable slevy (minimum: sleva na poplatníka = 30 840 CZK/year).

### Rule 6 — DAP ř. 84: Withheld advances (sražené zálohy)
```
DAP ř. 84 = SUM(total_tax_advance) across all POZP documents
```
Use `total_tax_advance` (ř. 8) — it already aggregates ř. 6 + ř. 7.

### Rule 7 — Overpayment / Underpayment
```
result = DAP ř. 71 − DAP ř. 84

result < 0  → Přeplatek (refund) — claim via DAP 7. oddíl
result > 0  → Nedoplatek (payment due)
result = 0  → No action required
```

---

## Multiple Employer Handling

When a taxpayer has more than one POZP (worked for multiple employers during the year):

1. **Sum** `tax_base` (ř. 5) from all POZP documents → write total to **DAP ř. 36**
2. **Sum** `total_tax_advance` (ř. 8) from all POZP documents → write total to **DAP ř. 84**
3. **Sum** `monthly_tax_bonuses` (ř. 9) from all POZP documents → write total to **DAP ř. 75**
4. Attach all POZP documents as enclosures (přílohy) to the DAP submission

---

## Validation Checks

Before finalising DAP, verify:

- [ ] `tax_base` (ř. 5) on each POZP == `incomes_paid_till_january_31` (ř. 2) + `additional_payments` (ř. 4)
- [ ] `total_tax_advance` (ř. 8) == `tax_advance_from_row_2` (ř. 6) + `tax_advance_from_row_4` (ř. 7)
- [ ] DAP ř. 36 equals the sum of `tax_base` across all POZP documents
- [ ] DAP ř. 84 equals the sum of `total_tax_advance` across all POZP documents
- [ ] `accounted_in_months` coverage is consistent (no gaps or overlaps between employers)

---

## Standard Slevy (Credits) to Apply

| DAP line | Credit | Amount (2025) | Condition |
|---|---|---|---|
| **ř. 64a** | Sleva na poplatníka | 30 840 CZK | Always — every taxpayer |
| **ř. 65a** | Sleva na manžel(k)u | 24 840 CZK | Partner income < 68 000 CZK/year AND caring for child under 3 |
| **ř. 65b** | Sleva na manžel(k)u ZTP/P | 49 680 CZK | Partner holds ZTP/P card |
| **ř. 66** | Invalidita I.–II. stupeň | 2 520 CZK | Taxpayer holds invalidity certificate |
| **ř. 67** | Invalidita III. stupeň | 5 040 CZK | Taxpayer holds invalidity certificate III |
| **ř. 68** | ZTP/P | 16 140 CZK | Taxpayer holds ZTP/P card |

---

## Source of Truth

- Czech law: Zákon č. 586/1992 Sb. o daních z příjmů
- Relevant sections: § 5 (základ daně), § 6 (závislá činnost), § 16 (sazba daně), § 35ba (slevy)
- Form: MFin 5460 — Potvrzení o zdanitelných příjmech ze závislé činnosti
- 2026 threshold (36 × průměrná mzda): **CZK 1 762 812**
