# Tax Calculator – Project Guidelines

## Overview

A FastAPI application that accepts PDF documents (invoices, receipts, tax forms), extracts their content, and calculates taxes according to Czech Republic tax law.

## Tech Stack

- **Language**: Python 3
- **Framework**: FastAPI with Uvicorn
- **PDF Processing**: Scanned PDFs use OCR (`pytesseract` + `pdf2image`); text-based PDFs use direct text extraction
- **Package management**: uv with `requirements.txt`
- **Environment**: Nix (`shell.nix`) with direnv (`.envrc`) for system dependencies (`tesseract`, `poppler-utils`); Python venv (`.venv`) for uv-managed packages

## Code Style

- Follow PEP 8
- Use type hints for all function signatures
- Use `async def` for FastAPI route handlers
- Prefer f-strings for string formatting

## Architecture

- `main.py` — Application entry point, FastAPI app and route definitions
- PDF upload → text extraction (OCR for scanned, direct for text-based) → parsing → tax calculation → response
- All monetary values use `Decimal` to avoid floating-point errors
- Tax rates and rules follow Czech Republic legislation (zákon o daních z příjmů, DPH)

## Build and Test

```bash
# Enter the Nix environment (installs system deps + activates .venv)
nix-shell

# Or use direnv (automatic via .envrc)
direnv allow

# Install Python dependencies
uv pip install -r requirements.txt

# Run the development server
fastapi dev

# Run tests
pytest
```

## Custom Agents

- **frontend-planner** — Plans Next.js frontend features; hands off to frontend-coder and frontend-tester
- **frontend-coder** — Implements Next.js frontend changes; outputs structured JSON status
- **frontend-tester** — Validates Next.js frontend changes; outputs structured JSON results

## Conventions

- Validate uploaded files: only accept `application/pdf` content type
- Return structured JSON responses from all endpoints
- Use `HTTPException` for error responses with appropriate status codes
- Keep tax calculation logic separate from PDF parsing logic
- All tax amounts are in CZK (Czech Koruna)

## Domain Context

- **DPH** (Daň z přidané hodnoty) — Czech VAT, standard rate 21%, reduced rates 12% and 0%
- **DPFO** (Daň z příjmů fyzických osob) — Personal income tax
- **DPPO** (Daň z příjmů právnických osob) — Corporate income tax
- When referencing Czech tax law, use the correct Czech terminology alongside English explanations
