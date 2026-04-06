import os
from typing import Any

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.config import load_dotenv_file
from backend.routers.pdf import router as pdf_router


def _env_flag(name: str, default: bool = False) -> bool:
    value = os.getenv(name)
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


def _is_dev_mode(app_env: str) -> bool:
    return app_env.strip().lower() in {"dev", "development", "local"}


def _parse_allowed_origins() -> list[str]:
    allowed_origins = os.getenv("CORS_ALLOWED_ORIGINS", "")
    return [origin.strip() for origin in allowed_origins.split(",") if origin.strip()]


def _cors_settings() -> dict[str, Any]:
    app_env = os.getenv("APP_ENV", "production")
    allow_all = _env_flag("CORS_ALLOW_ALL", default=False)

    if _is_dev_mode(app_env) or allow_all:
        return {
            "allow_origins": ["*"],
            "allow_credentials": False,
            "allow_methods": ["*"],
            "allow_headers": ["*"],
        }

    return {
        "allow_origins": _parse_allowed_origins(),
        "allow_credentials": True,
        "allow_methods": ["*"],
        "allow_headers": ["*"],
    }


def create_app() -> FastAPI:
    load_dotenv_file()
    app = FastAPI()
    app.add_middleware(CORSMiddleware, **_cors_settings())
    app.include_router(pdf_router)
    return app


app = create_app()
