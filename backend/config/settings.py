from __future__ import annotations

import os
from decimal import Decimal, InvalidOperation
from functools import lru_cache
from pathlib import Path

_ENV_ANNUAL_THRESHOLD_CZK = "ANNUAL_THRESHOLD_CZK"
_DOTENV_PATH = Path(__file__).resolve().parents[2] / ".env"


@lru_cache(maxsize=1)
def _load_dotenv_file() -> None:
    """Load environment variables from the repository .env file once."""
    if not _DOTENV_PATH.exists():
        return

    for raw_line in _DOTENV_PATH.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue

        if line.startswith("export "):
            line = line[len("export ") :].strip()

        if "=" not in line:
            continue

        key, value = line.split("=", 1)
        key = key.strip()
        if not key:
            continue

        os.environ.setdefault(key, value.strip())


def load_dotenv_file() -> None:
    """Public entry point for loading repository .env variables."""
    _load_dotenv_file()


def get_tax_annual_threshold_czk() -> Decimal:
    """Return annual progressive tax threshold in CZK from environment.

    Raises:
        ValueError: If ANNUAL_THRESHOLD_CZK is missing, blank, non-numeric, or non-positive.
    """
    load_dotenv_file()

    raw_value = os.getenv(_ENV_ANNUAL_THRESHOLD_CZK)

    if raw_value is None or raw_value.strip() == "":
        raise ValueError(
            f"Missing required {_ENV_ANNUAL_THRESHOLD_CZK}. Set it in environment or .env."
        )

    try:
        value = Decimal(raw_value)
    except InvalidOperation as exc:
        raise ValueError(
            f"Invalid {_ENV_ANNUAL_THRESHOLD_CZK}: '{raw_value}'. Must be numeric."
        ) from exc

    if value <= 0:
        raise ValueError(
            f"Invalid {_ENV_ANNUAL_THRESHOLD_CZK}: '{raw_value}'. Must be positive."
        )

    return value
