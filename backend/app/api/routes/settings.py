"""Settings status endpoint."""

from fastapi import APIRouter

from app.config import get_settings
from app.schemas import SettingsStatusResponse
from app.services.bright_data import BrightDataService

router = APIRouter(prefix="/api/settings", tags=["settings"])


@router.get("/status", response_model=SettingsStatusResponse)
def settings_status():
    settings = get_settings()
    bright_data = BrightDataService()
    data_mode = "live" if bright_data.is_available else "unavailable"

    return SettingsStatusResponse(
        default_country=settings.default_country,
        default_language=settings.default_language,
        default_locale=settings.default_locale,
        default_currency=settings.default_currency,
        bright_data_configured=settings.has_bright_data,
        openai_configured=settings.has_openai,
        codex_enabled=settings.codex_agents_enabled,
        database_status="connected",
        backend_api_url="http://localhost:8000",
        data_mode=data_mode,
    )
