# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Changed
- **BREAKING:** `/calculate-tax` now accepts a single ZIP archive instead of multiple PDFs (`routers/pdf.py`)
  - Previous: `curl -F "files=@employer-a.pdf" -F "files=@employer-b.pdf" http://localhost:8000/calculate-tax`
  - Current: `curl -F "file=@all-pozp.zip" http://localhost:8000/calculate-tax`
  - Automatically filters out macOS metadata (`__MACOSX/` folders) and dotfiles (`.DS_Store`)
  - Supports multiple PDFs in a single ZIP for aggregating multiple employers

### Removed
- **BREAKING:** Removed `/upload-pdf` endpoint (previously returned raw extracted fields without tax calculation)
  - Use `/calculate-tax` instead — the `confirmations` array in the response contains the extracted fields from each PDF

### Fixed
- Type safety: Fixed Pyright type checker errors in `services/pdf_service.py` where `accounted_in_months` (str | None) was incorrectly receiving union type `Decimal | str | None`
- Type safety: Fixed test factory functions to explicitly pass `None` for all optional fields in `ConfirmationOfATaxableIncome`
- Cross-platform compatibility: ZIP processing now ignores platform-specific metadata (macOS `__MACOSX/`, Windows Thumbs.db patterns)

## [0.1.0] - 2025-03-18

### Added
- Initial release with FastAPI-based Czech tax calculator
- PDF parsing for "Potvrzení o zdanitelných příjmech" (MFin 5460) using pdfplumber
- DAP-compliant tax calculation (15% / 23% progressive rates)
- Support for multiple employers via aggregation
- Automatic sleva na poplatníka (CZK 30,840)
- Overpayment/underpayment detection
