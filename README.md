# Tax Calculator

A FastAPI application that parses Czech tax forms (Potvrzení o zdanitelných příjmech / MFin 5460), extracts income and tax advance data from PDF documents, and calculates annual income tax according to 2026 Czech Republic tax law.

## Features

- **PDF parsing** — Extracts structured data from the 2025 "Potvrzení o zdanitelných príjmech" (MFin 5460) using `pdfplumber`
- **DAP-compliant tax calculation** — Computes DPFO (daň z příjmů fyzických osob) following Czech tax return rules:
  - Tax base rounded down to nearest 100 CZK before applying rates (DAP ř. 56)
  - Progressive rates: 15 % on first CZK 1 762 812, 23 % above (DAP ř. 57)
  - Automatic sleva na poplatníka (30 840 CZK) applied (DAP ř. 70)
  - Tax after credits computed with MAX(0, tax − credits) (DAP ř. 71)
- **Overpayment detection** — Compares tax after credits against withheld advances to determine refund (přeplatek) or underpayment (nedoplatek)
- **All monetary values** use `Decimal` — no floating-point errors

## API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| `POST` | `/calculate-tax` | Upload a ZIP archive containing POZP PDFs, extract fields, and calculate annual income tax |

See [docs/api.md](docs/api.md) for detailed request/response schemas and `curl` examples.

## Quick Start

```bash
# 1. Enter the Nix environment (or use direnv allow)
nix-shell

# 2. Install Python dependencies
pip install -r requirements.txt

# 3. Run the dev server
fastapi dev

# 4. Create a ZIP with one or more POZP PDFs
zip pozp-documents.zip MSFT-POZP-2025-1.pdf MSFT-POZP-2025-2.pdf

# 5. Upload the ZIP and calculate tax
curl -F "file=@pozp-documents.zip" http://localhost:8000/calculate-tax
```

Example response:

```json
{
  "confirmations": [{
    "incomes_paid_till_january_31": "1704925",
    "accounted_in_months": "05 06 07 08 09 10 11 12",
    "additional_payments": "0",
    "tax_base": "1704925",
    "total_tax_advance": "282298",
    "monthly_tax_bonuses": "0"
  }],
  "total_employment_income": "1704925",
  "partial_tax_base": "1704925",
  "rounded_tax_base": "1704900",
  "income_tax": "255735",
  "total_tax_credits": "30840",
  "tax_after_credits": "224895",
  "advances_withheld": "282298",
  "overpayment_or_underpayment": "-57403"
}
```

A negative `overpayment_or_underpayment` means a refund (přeplatek) — `tax_after_credits` is less than the withheld advances.

## Czech Tax Context

| Czech Term | English | Value (2026) |
|---|---|---|
| DPFO — Daň z příjmů fyzických osob | Personal income tax | 15 % / 23 % |
| Základ daně | Tax base | ř. 2 + ř. 4 |
| Sražená záloha | Withheld tax advance | rows 6–8 |
| Sleva na poplatníka | Taxpayer credit | 30 840 CZK/year |
| Přeplatek | Overpayment (refund) | tax after credits − advances < 0 |
| Nedoplatek | Underpayment | tax after credits − advances > 0 |
| Potvrzení o zdanitelných příjmech | Certificate of taxable incomes | MFin 5460 |
| DAP — Daňové přiznání | Tax return form | Přiznání k dani z příjmů FO |

## Prerequisites

- [Nix](https://nixos.org/download/) package manager
- [direnv](https://direnv.net/docs/installation.html) (recommended)

## Setup

```bash
# Option A: direnv (recommended — auto-loads on cd)
direnv allow

# Option B: nix-shell (current terminal only)
nix-shell
```

Both options provide system dependencies (`poppler-utils`, `git`), create a `.venv/`, and install pip packages.

## Development

```bash
# Run the dev server (auto-reload)
fastapi dev

# Run tests
pytest

# Type checking
mypy --explicit-package-bases models/ services/ routers/ --ignore-missing-imports
```

In VS Code, you can also use `Terminal` -> `Run Task...` -> `Run FastAPI app` to start the server on port `8000` without creating a custom local task.

## Project Structure

```
main.py                                — FastAPI app entry point
routers/pdf.py                         — /calculate-tax endpoint (ZIP archive upload)
models/
  confirmation_of_a_taxable_income.py  — Pydantic model for MFin 5460 form fields
  tax_result.py                        — Pydantic model for tax calculation result
services/
  pdf_service.py                       — PDF table extraction (pdfplumber)
  tax_calculation_service.py           — Progressive tax computation (15%/23%)
tests/
  test_tax_calculation_service.py      — Unit tests for tax calculation
  test_calculate_tax_endpoint.py       — Integration tests for API endpoints
```
