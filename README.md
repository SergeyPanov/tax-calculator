# Tax Calculator

A FastAPI application that parses Czech tax forms (Potvrzení o zdanitelných příjmech / MFin 5460), extracts income and tax advance data from PDF documents, and calculates annual income tax according to 2026 Czech Republic tax law.

## Features

- **PDF parsing** — Extracts structured data from the 2025 "Potvrzení o zdanitelných příjmech" form using `pdfplumber`
- **Tax calculation** — Computes DPFO (daň z příjmů fyzických osob) using 2026 progressive rates:
  - 15 % on the first CZK 1 762 812 of the tax base (základ daně)
  - 23 % on income above CZK 1 762 812
- **Overpayment detection** — Compares computed tax against withheld advances (sražené zálohy) to determine refund or underpayment
- **All monetary values** use `Decimal` — no floating-point errors

## API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| `POST` | `/upload-pdf` | Upload a PDF and extract fields from the confirmation form |
| `POST` | `/calculate-tax` | Upload a PDF, extract fields, and calculate annual income tax |

See [docs/api.md](docs/api.md) for detailed request/response schemas and `curl` examples.

## Quick Start

```bash
# 1. Enter the Nix environment (or use direnv allow)
nix-shell

# 2. Install Python dependencies
pip install -r requirements.txt

# 3. Run the dev server
fastapi dev

# 4. Upload a confirmation PDF and calculate tax
curl -F "file=@MSFT-POZP-2025.pdf" http://localhost:8000/calculate-tax
```

Example response:

```json
{
  "confirmations": [{
    "incomes_paid_till_january_31": "1704925",
    "accounted_in_months": "05 06 07 08 09 10 11 12",
    "additional_payments": "0",
    "tax_base": "1704925",
    "tax_advance_from_row_2": "282298",
    "tax_advance_from_row_4": "0",
    "total_tax_advance": "282298",
    "monthly_tax_bonuses": "0"
  }],
  "aggregated_tax_base": "1704925",
  "aggregated_advances_withheld": "282298",
  "tax_at_15_pct": "255738",
  "tax_at_23_pct": "0",
  "total_tax": "255738",
  "overpayment_or_underpayment": "-26560"
}
```

A negative `overpayment_or_underpayment` means a refund (přeplatek) — the employer withheld more than the actual tax.

## Czech Tax Context

| Czech Term | English | Value (2026) |
|---|---|---|
| DPFO — Daň z příjmů fyzických osob | Personal income tax | 15 % / 23 % |
| Základ daně | Tax base | ř. 2 + ř. 4 |
| Sražená záloha | Withheld tax advance | rows 6–8 |
| Přeplatek | Overpayment (refund) | tax − advances < 0 |
| Nedoplatek | Underpayment | tax − advances > 0 |
| Potvrzení o zdanitelných příjmech | Certificate of taxable incomes | MFin 5460 |

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

## Project Structure

```
main.py                                — FastAPI app entry point
routers/pdf.py                         — /upload-pdf and /calculate-tax endpoints
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
