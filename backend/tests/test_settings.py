from decimal import Decimal
from pathlib import Path
from typing import Protocol, cast

import pytest

from backend.config import get_tax_annual_threshold_czk
from backend.config import settings as settings_module


class _SupportsCacheClear(Protocol):
    def __call__(self) -> None: ...

    def cache_clear(self) -> None: ...


def _reset_dotenv_loader_state() -> None:
    loader = cast(_SupportsCacheClear, settings_module._load_dotenv_file)
    loader.cache_clear()


def _legacy_threshold_env_key() -> str:
    return "_".join(["TAX", "ANNUAL", "THRESHOLD", "CZK"])


def _clear_threshold_env(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("ANNUAL_THRESHOLD_CZK", raising=False)
    monkeypatch.delenv(_legacy_threshold_env_key(), raising=False)


def test_threshold_raises_when_env_and_dotenv_missing(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    _clear_threshold_env(monkeypatch)
    dotenv_path = tmp_path / ".env"
    monkeypatch.setattr(settings_module, "_DOTENV_PATH", dotenv_path)
    _reset_dotenv_loader_state()

    try:
        with pytest.raises(ValueError, match="Missing required ANNUAL_THRESHOLD_CZK"):
            get_tax_annual_threshold_czk()
    finally:
        _reset_dotenv_loader_state()


def test_threshold_uses_annual_threshold_env_value(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _clear_threshold_env(monkeypatch)
    monkeypatch.setenv("ANNUAL_THRESHOLD_CZK", "1800000")

    assert get_tax_annual_threshold_czk() == Decimal("1800000")


@pytest.mark.parametrize("invalid_value", ["", "abc", "0", "-1"])
def test_threshold_rejects_invalid_annual_threshold_values(
    monkeypatch: pytest.MonkeyPatch,
    invalid_value: str,
) -> None:
    _clear_threshold_env(monkeypatch)
    monkeypatch.setenv("ANNUAL_THRESHOLD_CZK", invalid_value)

    with pytest.raises(ValueError):
        get_tax_annual_threshold_czk()


def test_loads_threshold_from_dotenv_file_when_env_unset(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    _clear_threshold_env(monkeypatch)
    dotenv_path = tmp_path / ".env"
    dotenv_path.write_text("ANNUAL_THRESHOLD_CZK=1999999\n", encoding="utf-8")
    monkeypatch.setattr(settings_module, "_DOTENV_PATH", dotenv_path)
    _reset_dotenv_loader_state()

    try:
        assert get_tax_annual_threshold_czk() == Decimal("1999999")
    finally:
        _reset_dotenv_loader_state()


def test_dotenv_parser_handles_comments_export_and_invalid_lines(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    _clear_threshold_env(monkeypatch)
    dotenv_path = tmp_path / ".env"
    dotenv_path.write_text(
        "\n"
        "# a comment line should be ignored\n"
        "export ANNUAL_THRESHOLD_CZK=1676052\n"
        "MALFORMED_WITHOUT_EQUALS\n"
        " =value_without_key\n",
        encoding="utf-8",
    )
    monkeypatch.setattr(settings_module, "_DOTENV_PATH", dotenv_path)
    _reset_dotenv_loader_state()

    try:
        assert get_tax_annual_threshold_czk() == Decimal("1676052")
    finally:
        _reset_dotenv_loader_state()


def test_legacy_threshold_env_is_not_used_as_source(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    _clear_threshold_env(monkeypatch)
    monkeypatch.setenv(_legacy_threshold_env_key(), "1700000")

    dotenv_path = tmp_path / ".env"
    monkeypatch.setattr(settings_module, "_DOTENV_PATH", dotenv_path)
    _reset_dotenv_loader_state()

    try:
        with pytest.raises(ValueError, match="Missing required ANNUAL_THRESHOLD_CZK"):
            get_tax_annual_threshold_czk()
    finally:
        _reset_dotenv_loader_state()
