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
uv pip install -r requirements.txt

# 3. Run the dev server
fastapi dev backend/main.py

# 4. Create a ZIP with one or more POZP PDFs
zip pozp-documents.zip employer-a-pozp.pdf employer-b-pozp.pdf

# 5. Upload the ZIP and calculate tax
curl -F "file=@pozp-documents.zip" http://localhost:8000/calculate-tax
```

Example response (synthetic values):

```json
{
  "confirmations": [{
    "incomes_paid_till_january_31": "1234500",
    "accounted_in_months": "05 06 07 08 09 10 11 12",
    "additional_payments": "0",
    "tax_base": "1234500",
    "total_tax_advance": "185000",
    "monthly_tax_bonuses": "0"
  }],
  "total_employment_income": "1234500",
  "partial_tax_base": "1234500",
  "rounded_tax_base": "1234500",
  "income_tax": "185175",
  "total_tax_credits": "30840",
  "tax_after_credits": "154335",
  "advances_withheld": "185000",
  "overpayment_or_underpayment": "-30665"
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


## CORS Configuration

Backend CORS behavior is controlled by environment variables:

- `APP_ENV` — environment mode (`development` / `local` => permissive CORS for local work)
- `CORS_ALLOW_ALL` — if `true`, backend allows all origins (`*`) and disables credentials to keep CORS valid
- `CORS_ALLOWED_ORIGINS` — comma-separated allowlist used in non-dev mode (for example: `https://app.example.cz,https://admin.example.cz`)

Default behavior is secure: if no variables are set, backend runs in non-dev mode with an explicit allowlist requirement.

### Local Docker verification

```bash
# Start both services with local dev CORS env from docker-compose.yml
docker compose up --build

# Verify CORS preflight from frontend origin
curl -i -X OPTIONS http://localhost:8000/calculate-tax   -H "Origin: http://localhost:3000"   -H "Access-Control-Request-Method: POST"
```

Expected in local dev: `access-control-allow-origin: *` in the response headers.

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

Both options provide system dependencies (`poppler-utils`, `git`), create a `.venv/`, and install packages via uv.

## Development

```bash
# Run the dev server (auto-reload)
fastapi dev backend/main.py

# Run tests
pytest backend/tests/ -v

# Type checking
mypy --explicit-package-bases backend/models backend/services backend/routers --ignore-missing-imports
```

In VS Code, you can also use `Terminal` -> `Run Task...` -> `Run FastAPI app` to start the server on port `8000` without creating a custom local task.

## Project Structure

```
backend/main.py                        — FastAPI app entry point
backend/routers/pdf.py                 — /calculate-tax endpoint (ZIP archive upload)
backend/models/
  confirmation_of_a_taxable_income.py  — Pydantic model for MFin 5460 form fields
  tax_result.py                        — Pydantic model for tax calculation result
backend/services/
  pdf_service.py                       — PDF table extraction (pdfplumber)
  tax_calculation_service.py           — Progressive tax computation (15%/23%)
backend/tests/
  test_tax_calculation_service.py      — Unit tests for tax calculation
  test_calculate_tax_endpoint.py       — Integration tests for API endpoints
```
