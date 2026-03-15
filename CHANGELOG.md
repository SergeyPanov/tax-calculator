# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

## [0.2.0] — 2026-03-15

### Added
- `POST /calculate-tax` endpoint — uploads a PDF, extracts fields, and computes annual DPFO income tax using 2026 progressive rates (15 %/23 %)
- `TaxResult` model (`models/tax_result.py`) with aggregated tax base, bracket taxes, and overpayment/underpayment
- `TaxCalculationService` (`services/tax_calculation_service.py`) implementing progressive tax calculation with `ROUND_FLOOR` rounding
- Unit tests for tax calculation (6 cases: below threshold, above threshold, multi-employer, None fields, empty list, overpayment)
- Integration tests for `/calculate-tax` and `/upload-pdf` endpoints
- API documentation (`docs/api.md`)
- Documentation agent (`.github/agents/docs.agent.md`)

### Changed
- `ConfirmationOfATaxableIncome` model updated to match the 2025 MFin 5460 form layout:
  - Removed obsolete fields: `additional_payments_2005_2007`, `additional_payments_2008_2011`, `total_compulsory_premium_insurance`, `total_employer_premium_insurance`
  - Added new fields: `additional_payments`, `total_tax_advance`, `monthly_tax_bonuses`
  - Changed `accounted_in_months` from `Decimal` to `str`
- `ROW_FIELD_MAP` in `PdfService` updated to match 2025 form row numbering (tax base = row 5, advances = rows 6–8)
- Added row-1 detection by Czech label text (form has no "1." prefix)
- Added X-filler cell skipping in PDF table extraction (`_last_non_empty`)

### Fixed
- All extracted values were mapped to wrong fields due to stale `ROW_FIELD_MAP` designed for an older form version

## [0.1.0] — 2026-03-14

### Added
- `POST /upload-pdf` endpoint — uploads a PDF and extracts fields from "Potvrzení o zdanitelných příjmech"
- `ConfirmationOfATaxableIncome` model with Pydantic validation
- `PdfService` with `pdfplumber`-based table extraction
- Nix + direnv development environment (`shell.nix`, `.envrc`)
