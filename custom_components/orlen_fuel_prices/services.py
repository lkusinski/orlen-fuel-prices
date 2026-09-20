"""Services for the Ceny Paliw Orlen integration."""
from __future__ import annotations

import logging

import voluptuous as vol
from homeassistant.core import HomeAssistant, ServiceCall, SupportsResponse
from homeassistant.helpers import config_validation as cv

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

SERVICE_GET_PRICES = "get_prices"

GET_PRICES_SCHEMA = vol.Schema(
    {
        vol.Optional("entry_id"): cv.string,
    }
)


def _resolve_coordinator(hass: HomeAssistant, entry_id: str | None):
    entries = hass.data.get(DOMAIN, {})
    if not entries:
        raise vol.Invalid("no Ceny Paliw Orlen config entry loaded")
    if entry_id:
        if entry_id not in entries:
            raise vol.Invalid(f"unknown entry_id: {entry_id}")
        return entries[entry_id]["coordinator"]
    return next(iter(entries.values()))["coordinator"]


async def _async_handle_get_prices(call: ServiceCall) -> dict:
    coordinator = _resolve_coordinator(call.hass, call.data.get("entry_id"))
    data = coordinator.data or {}
    return {
        "motor": data.get("motor", {}),
        "lpg": data.get("lpg", {}),
        "vat_rate": data.get("vat_rate"),
        "margin": data.get("margin"),
        "fetched_at": data.get("fetched_at"),
        "source": "ORLEN hurtowe ceny paliw (netto), brutto = netto x (1 + VAT)",
    }


async def async_setup_services(hass: HomeAssistant) -> None:
    """Register the get_prices service once."""
    if hass.services.has_service(DOMAIN, SERVICE_GET_PRICES):
        return
    hass.services.async_register(
        DOMAIN,
        SERVICE_GET_PRICES,
        _async_handle_get_prices,
        schema=GET_PRICES_SCHEMA,
        supports_response=SupportsResponse.ONLY,
    )
