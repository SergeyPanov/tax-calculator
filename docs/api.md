# API Documentation

Base URL: `http://localhost:8000`

---

## POST /calculate-tax

Upload a ZIP archive containing one or more "Potvrzení o zdanitelných příjmech" (MFin 5460) PDFs, extract fields from each, aggregate values, and compute annual income tax using the 2026 DPFO progressive rates.

### Request

Multipart form with a single ZIP file containing one or more PDF files.

```bash
# Single employer (one PDF in ZIP)
zip pozp.zip MSFT-POZP-2025.pdf
curl -F "file=@pozp.zip" http://localhost:8000/calculate-tax

# Multiple employers (multiple PDFs in ZIP)
zip pozp-all.zip employer-a.pdf employer-b.pdf
curl -F "file=@pozp-all.zip" http://localhost:8000/calculate-tax
```

**Note:** The ZIP archive can be created on any platform. macOS metadata files (`__MACOSX/` folders, `.DS_Store`) are automatically filtered out.

### Response `200 OK`

```json
{
  "confirmations": [
    {
      "total_accounted_incomes": null,
      "incomes_paid_till_january_31": "1704925",
      "accounted_in_months": "05 06 07 08 09 10 11 12",
      "additional_payments": "0",
      "tax_base": "1704925",
      "tax_advance_from_row_2": "282298",
      "tax_advance_from_row_4": "0",
      "total_tax_advance": "282298",
      "monthly_tax_bonuses": "0"
    }
  ],
  "total_employment_income": "1704925",
  "partial_tax_base": "1704925",
  "rounded_tax_base": "1704900",
  "income_tax": "255735",
  "total_tax_credits": "30840",
  "tax_after_credits": "224895",
  "advances_withheld": "282298",
  "overpayment_or_underpayment": "-57403",
  "aggregated_tax_base": "1704925",
  "aggregated_advances_withheld": "282298",
  "tax_at_15_pct": "255735",
  "tax_at_23_pct": "0",
  "total_tax": "255735"
}
```

### Response Fields

| Field | Type | DAP Row | Description |
|---|---|---|---|
| `confirmations` | `list` | — | Parsed data from each PDF in the uploaded ZIP archive |
| `total_employment_income` | `Decimal` | ř. 31 | Sum of incomes + additional payments across all confirmations |
| `partial_tax_base` | `Decimal` | ř. 36 | Sum of `tax_base` (partial tax base from dependent activity § 6) |
| `rounded_tax_base` | `Decimal` | ř. 56 | `partial_tax_base` rounded down to nearest 100 CZK |
| `income_tax` | `Decimal` | ř. 57 | Progressive tax computed from `rounded_tax_base` (15 %/23 %) |
| `total_tax_credits` | `Decimal` | ř. 70 | Sum of applied tax credits (slevy) — currently only sleva na poplatníka: 30 840 CZK |
| `tax_after_credits` | `Decimal` | ř. 71 | Income tax after credits: `MAX(0, income_tax − total_tax_credits)` |
| `advances_withheld` | `Decimal` | ř. 84 | Sum of `total_tax_advance` across all confirmations (sražené zálohy) |
| `overpayment_or_underpayment` | `Decimal` | — | `tax_after_credits − advances_withheld`; negative = refund (přeplatek) |
| `aggregated_tax_base` | `Decimal` | — | *(legacy)* Alias for `partial_tax_base` |
| `aggregated_advances_withheld` | `Decimal` | — | *(legacy)* Alias for `advances_withheld` |
| `tax_at_15_pct` | `Decimal` | — | Tax at 15 % on the first CZK 1 762 812 of `rounded_tax_base` |
| `tax_at_23_pct` | `Decimal` | — | Tax at 23 % on `rounded_tax_base` exceeding CZK 1 762 812 |
| `total_tax` | `Decimal` | — | `tax_at_15_pct + tax_at_23_pct` (before applying credits) |

#### Confirmation Fields (each PDF in `confirmations` array)

| Field | Type | Form Row | Czech Label | Description |
|---|---|---|---|---|
| `total_accounted_incomes` | `Decimal \| null` | 1 | Úhrn zúčtovaných příjmů | Total accounted incomes from dependent activity |
| `incomes_paid_till_january_31` | `Decimal \| null` | 2 | Příjmy vyplacené do 31. 1. | Incomes from row 1 paid by 31 January |
| `accounted_in_months` | `string \| null` | 3 | Zúčtováno v měsících | Months worked (e.g. `"01 02 03"`) |
| `additional_payments` | `Decimal \| null` | 4 | Doplatky příjmů | Additional payments (§ 5 subsection 4) |
| `tax_base` | `Decimal \| null` | 5 | Základ daně | Tax base (row 2 + row 4) |
| `tax_advance_from_row_2` | `Decimal \| null` | 6 | Sražená záloha z ř. 2 | Tax advance withheld from row 2 incomes |
| `tax_advance_from_row_4` | `Decimal \| null` | 7 | Sražená záloha z ř. 4 | Tax advance withheld from row 4 incomes |
| `total_tax_advance` | `Decimal \| null` | 8 | Záloha celkem | Total tax advance (row 6 + row 7) |
| `monthly_tax_bonuses` | `Decimal \| null` | 9 | Měsíční daňové bonusy | Monthly tax bonuses paid out |

### Tax Formula (DAP-Compliant)

```
1. rounded_tax_base = ⌊partial_tax_base / 100⌋ × 100  (round down to nearest 100 CZK)

2. If rounded_tax_base ≤ 1 762 812:
       income_tax = ⌊rounded_tax_base × 0.15⌋
   
   If rounded_tax_base > 1 762 812:
       income_tax = ⌊1 762 812 × 0.15⌋ + ⌊(rounded_tax_base − 1 762 812) × 0.23⌋

3. total_tax_credits = 30 840  (sleva na poplatníka — always applied)

4. tax_after_credits = MAX(0, income_tax − total_tax_credits)

5. overpayment_or_underpayment = tax_after_credits − advances_withheld
```

**Example** (CZK 1 704 925 tax base, CZK 282 298 withheld):
```
rounded_tax_base    = ⌊1 704 925 / 100⌋ × 100 = 1 704 900
income_tax          = ⌊1 704 900 × 0.15⌋      = 255 735
tax_after_credits   = MAX(0, 255 735 − 30 840) = 224 895
overpayment         = 224 895 − 282 298        = −57 403  (refund)
```

All amounts are rounded down (`ROUND_FLOOR`) to whole CZK per Czech tax law (§ 16 zákona č. 586/1992 Sb.).

### Errors

| Status | Detail | Cause |
|---|---|---|
| `400` | `"File must be a ZIP archive."` | Uploaded file is not `application/zip` or `application/x-zip-compressed` |
| `400` | `"Invalid ZIP archive."` | ZIP file is corrupted or unreadable |
| `400` | `"No PDF files found in the uploaded zip archive."` | ZIP contains no `.pdf` files (or only metadata files like `__MACOSX/`) |
| `400` | `"Failed to parse '...'..."` | A PDF inside the ZIP is corrupted or has an unrecognizable table layout |

---

## Multiple Employers / Multiple PDFs

When a taxpayer worked for multiple employers during the year, collect all "Potvrzení o zdanitelných příjmech" PDFs, add them to a single ZIP archive, and upload:

```bash
zip all-pozp.zip employer-a.pdf employer-b.pdf employer-c.pdf
curl -F "file=@all-pozp.zip" http://localhost:8000/calculate-tax
```

The API will:
1. Extract each PDF from the ZIP (ignoring `__MACOSX/` and hidden files)
2. Parse each POZP separately
3. **Aggregate** `tax_base` and `total_tax_advance` across all PDFs
4. Compute annual income tax on the **combined** tax base
5. Return `confirmations` array with all parsed PDFs + aggregated tax result

This follows Czech tax law: when a taxpayer has multiple POZPs from different employers, the tax bases and withheld advances must be summed before applying the progressive rate (§ 6 and § 36 odst. 1 zákona č. 586/1992 Sb.).
