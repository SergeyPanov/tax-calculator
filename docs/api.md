# API Documentation

Base URL: `http://localhost:8000`

---

## POST /upload-pdf

Extract fields from a "Potvrzení o zdanitelných příjmech" (MFin 5460) PDF without computing tax.

### Request

Multipart form with a single PDF file.

```bash
curl -F "file=@MSFT-POZP-2025.pdf" http://localhost:8000/upload-pdf
```

### Response `200 OK`

```json
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
```

### Response Fields

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

### Errors

| Status | Detail | Cause |
|---|---|---|
| `400` | `"File must be a PDF"` | Uploaded file is not `application/pdf` |
| `400` | `"Failed to parse PDF file..."` | PDF is corrupted or has an unrecognizable table layout |

---

## POST /calculate-tax

Upload a single "Potvrzení o zdanitelných příjmech" PDF, extract fields, and compute annual income tax using the 2026 DPFO progressive rates.

### Request

Multipart form with a single PDF file.

```bash
curl -F "file=@MSFT-POZP-2025.pdf" http://localhost:8000/calculate-tax
```

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
  "aggregated_tax_base": "1704925",
  "aggregated_advances_withheld": "282298",
  "tax_at_15_pct": "255738",
  "tax_at_23_pct": "0",
  "total_tax": "255738",
  "overpayment_or_underpayment": "-26560"
}
```

### Response Fields

| Field | Type | Description |
|---|---|---|
| `confirmations` | `list` | Parsed data from the uploaded confirmation(s) |
| `aggregated_tax_base` | `Decimal` | Sum of `tax_base` across all confirmations |
| `aggregated_advances_withheld` | `Decimal` | Sum of `total_tax_advance` across all confirmations |
| `tax_at_15_pct` | `Decimal` | Tax at 15 % on the first CZK 1 762 812 |
| `tax_at_23_pct` | `Decimal` | Tax at 23 % on income above CZK 1 762 812 |
| `total_tax` | `Decimal` | Total annual income tax (rounded down to whole CZK) |
| `overpayment_or_underpayment` | `Decimal` | `total_tax − aggregated_advances_withheld`; negative = refund (přeplatek) |

### Tax Formula

```
If tax_base ≤ 1 762 812:
    tax = ⌊tax_base × 0.15⌋

If tax_base > 1 762 812:
    tax = ⌊1 762 812 × 0.15⌋ + ⌊(tax_base − 1 762 812) × 0.23⌋

overpayment_or_underpayment = tax − advances_withheld
```

All amounts are rounded down (`ROUND_FLOOR`) to whole CZK per Czech tax law.

### Errors

| Status | Detail | Cause |
|---|---|---|
| `400` | `"File '...' is not a PDF"` | Uploaded file is not `application/pdf` |
| `400` | `"Failed to parse '...'..."` | PDF is corrupted or has an unrecognizable table layout |
