"""Diagnostics support for the Ceny Paliw Orlen integration."""
from __future__ import annotations

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from .const import DOMAIN

# No credentials are required by this integration, but keep masking in place so
# future additions never leak secrets through diagnostics.
TO_REDACT = {
    "password",
    "token",
    "device_token",
    "username",
    "email",
    "pat",
}


def _redact(value, key: str | None = None):
    if isinstance(value, dict):
        return {k: _redact(v, k) for k, v in value.items()}
    if isinstance(value, list):
        return [_redact(v, key) for v in value]
    if key and key.lower() in TO_REDACT:
        return "**REDACTED**"
    return value


async def async_get_config_entry_diagnostics(
    hass: HomeAssistant, entry: ConfigEntry
) -> dict:
    """Return diagnostics for a config entry."""
    coordinator = hass.data.get(DOMAIN, {}).get(entry.entry_id, {}).get(
        "coordinator"
    )
    return {
        "entry": {
            "title": entry.title,
            "data": _redact(dict(entry.data)),
            "options": _redact(dict(entry.options)),
        },
        "coordinator": {
            "last_update_success": getattr(coordinator, "last_update_success", None),
            "update_interval": str(getattr(coordinator, "update_interval", None)),
            "data": _redact(getattr(coordinator, "data", None)),
        },
    }
