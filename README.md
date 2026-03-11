# Tax Calculator

A FastAPI application that accepts PDF documents (invoices, receipts, tax forms), extracts their content via OCR, and calculates taxes according to Czech Republic tax law.

## Prerequisites

- [Nix](https://nixos.org/download/) package manager
- [direnv](https://direnv.net/docs/installation.html) (recommended for VS Code integration)

## Setup

### 1. Install Nix

Follow the official instructions at https://nixos.org/download/ to install Nix for your platform.

### 2. Clone and enter the project

```bash
git clone <repo-url>
cd tax-calculator
```

### 3. Option A: Using direnv (recommended)

direnv automatically loads the Nix environment whenever you `cd` into the project directory.

```bash
# Allow direnv for this project (one-time)
direnv allow
```

This will:
- Enter the Nix shell (providing `tesseract`, `poppler-utils`, `git`)
- Create a Python virtual environment in `.venv/` (if it doesn't exist)
- Activate the venv
- Install Python dependencies from `requirements.txt`

### 3. Option B: Using nix-shell directly

```bash
nix-shell
```

This performs the same steps as above but only for the current terminal session.

## Development in VS Code

### Recommended extensions

- [direnv](https://marketplace.visualstudio.com/items?itemName=mkhl.direnv) — loads the Nix environment automatically so the debugger and integrated terminal have access to system binaries like `tesseract`
- [Python](https://marketplace.visualstudio.com/items?itemName=ms-python.python) — Python language support, select `.venv` as the interpreter

### Running the dev server

```bash
fastapi dev
```

The server starts at http://127.0.0.1:8000 with auto-reload enabled.

### Debugging

With the direnv VS Code extension installed, the debugger inherits the Nix environment. Without it, launching from VS Code's debug console won't find `tesseract` on `PATH`.

## Project Structure

```
main.py            — FastAPI app entry point
routers/pdf.py     — PDF upload and OCR endpoint
shell.nix          — Nix environment (system dependencies)
.envrc             — direnv configuration (loads Nix shell)
requirements.txt   — Python dependencies
```
