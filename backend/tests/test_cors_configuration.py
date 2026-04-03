import importlib

from backend import main


def _reload_main_module() -> None:
    importlib.reload(main)


def test_dev_mode_is_permissive(monkeypatch) -> None:
    monkeypatch.setenv("APP_ENV", "development")
    monkeypatch.delenv("CORS_ALLOW_ALL", raising=False)
    monkeypatch.delenv("CORS_ALLOWED_ORIGINS", raising=False)

    _reload_main_module()
    settings = main._cors_settings()

    assert settings["allow_origins"] == ["*"]
    assert settings["allow_credentials"] is False


def test_non_dev_uses_explicit_allowlist(monkeypatch) -> None:
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
    monkeypatch.delenv("APP_ENV", raising=False)
    monkeypatch.delenv("CORS_ALLOW_ALL", raising=False)
    monkeypatch.delenv("CORS_ALLOWED_ORIGINS", raising=False)

    _reload_main_module()
    settings = main._cors_settings()

    assert settings["allow_origins"] == []
    assert settings["allow_credentials"] is True
