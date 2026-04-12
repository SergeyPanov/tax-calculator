import importlib

import pytest

from backend import main
from backend.config import settings as settings_module


def _reload_main_module() -> None:
    importlib.reload(main)


def _set_required_tax_threshold(monkeypatch) -> None:
    monkeypatch.setenv("ANNUAL_THRESHOLD_CZK", "1676052")


def _reset_dotenv_loader_state() -> None:
    cache_clear = getattr(settings_module._load_dotenv_file, "cache_clear", None)
    if callable(cache_clear):
        cache_clear()


def test_dev_mode_is_permissive(monkeypatch) -> None:
    _set_required_tax_threshold(monkeypatch)
    monkeypatch.setenv("APP_ENV", "development")
    monkeypatch.delenv("CORS_ALLOW_ALL", raising=False)
    monkeypatch.delenv("CORS_ALLOWED_ORIGINS", raising=False)

    _reload_main_module()
    settings = main._cors_settings()

    assert settings["allow_origins"] == ["*"]
    assert settings["allow_credentials"] is False


def test_non_dev_uses_explicit_allowlist(monkeypatch) -> None:
    _set_required_tax_threshold(monkeypatch)
    monkeypatch.setenv("APP_ENV", "production")
    monkeypatch.delenv("CORS_ALLOW_ALL", raising=False)
    monkeypatch.setenv(
        "CORS_ALLOWED_ORIGINS", "https://app.example.cz, https://admin.example.cz"
    )

    _reload_main_module()
    settings = main._cors_settings()

    assert settings["allow_origins"] == [
        "https://app.example.cz",
        "https://admin.example.cz",
    ]
    assert settings["allow_credentials"] is True


def test_non_dev_defaults_to_restrictive_empty_allowlist(monkeypatch) -> None:
    _set_required_tax_threshold(monkeypatch)
    monkeypatch.delenv("APP_ENV", raising=False)
    monkeypatch.delenv("CORS_ALLOW_ALL", raising=False)
    monkeypatch.delenv("CORS_ALLOWED_ORIGINS", raising=False)

    _reload_main_module()
    settings = main._cors_settings()

    assert settings["allow_origins"] == []
    assert settings["allow_credentials"] is True


def test_create_app_fails_fast_when_threshold_missing(monkeypatch, tmp_path) -> None:
    monkeypatch.delenv("ANNUAL_THRESHOLD_CZK", raising=False)
    dotenv_path = tmp_path / ".env"
    monkeypatch.setattr(settings_module, "_DOTENV_PATH", dotenv_path)
    _reset_dotenv_loader_state()

    try:
        with pytest.raises(ValueError, match="Missing required ANNUAL_THRESHOLD_CZK"):
            main.create_app()
    finally:
        _reset_dotenv_loader_state()
