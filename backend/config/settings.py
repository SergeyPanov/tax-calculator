from __future__ import annotations

import os
from decimal import Decimal, InvalidOperation
from pathlib import Path

_ENV_ANNUAL_THRESHOLD_CZK = "ANNUAL_THRESHOLD_CZK"
_DOTENV_PATH = Path(__file__).resolve().parents[2] / ".env"


def _iter_dotenv_lines(dotenv_path: Path) -> list[str]:
    """Return UTF-8 decoded .env file lines, or empty list when missing."""
    if not dotenv_path.exists():
        return []
    return dotenv_path.read_text(encoding="utf-8").splitlines()


def _parse_dotenv_assignment(raw_line: str) -> tuple[str, str] | None:
    """Parse a single dotenv assignment line into key/value pair."""
    line = raw_line.strip()
    if not line or line.startswith("#"):
        return None

    if line.startswith("export "):
        line = line[len("export ") :].strip()

    if "=" not in line:
        return None

    key, value = line.split("=", 1)
    key = key.strip()
    if not key:
        return None

    return key, value.strip()


def _load_dotenv_file() -> None:
    """Load repository .env variables without overriding process env."""
    for raw_line in _iter_dotenv_lines(_DOTENV_PATH):
        parsed = _parse_dotenv_assignment(raw_line)
        if parsed is None:
            continue
        key, value = parsed
        os.environ.setdefault(key, value)


def _noop_cache_clear() -> None:
    """Compatibility no-op for tests calling cache_clear()."""
    return None


_load_dotenv_file.cache_clear = _noop_cache_clear  # type: ignore[attr-defined]


def load_dotenv_file() -> None:
    """Public entry point for loading repository .env variables."""
    _load_dotenv_file()


def _get_required_env_value(name: str) -> str:
    """Return required env var value or raise explicit validation error."""
    raw_value = os.getenv(name)
    if raw_value is None or raw_value.strip() == "":
        raise ValueError(f"Missing required {name}. Set it in environment or .env.")
    return raw_value.strip()


def get_tax_annual_threshold_czk() -> Decimal:
    """Return annual progressive tax threshold in CZK from environment.

    Raises:
        ValueError: If ANNUAL_THRESHOLD_CZK is missing, blank, non-numeric, or non-positive.
    """
    load_dotenv_file()
    raw_value = _get_required_env_value(_ENV_ANNUAL_THRESHOLD_CZK)

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
