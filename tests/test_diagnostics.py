"""Tests for diagnostics redaction."""
from __future__ import annotations

from custom_components.orlen_fuel_prices.const import DOMAIN
from custom_components.orlen_fuel_prices.diagnostics import (
    async_get_config_entry_diagnostics,
)


class _Entry:
    title = "Ceny Paliw Orlen"
    entry_id = "e1"
    data = {"password": "secret", "device_token": "abc", "products": ["Pb95"]}
    options = {"margin": 0, "username": "user@example.com"}


async def test_diagnostics_redacts_secrets(fake_coordinator):
    hass = type("Hass", (), {})()
    hass.data = {DOMAIN: {"e1": {"coordinator": fake_coordinator}}}
    diag = await async_get_config_entry_diagnostics(hass, _Entry())
    assert diag["entry"]["data"]["password"] == "**REDACTED**"
    assert diag["entry"]["data"]["device_token"] == "**REDACTED**"
    assert diag["entry"]["data"]["products"] == ["Pb95"]
    assert diag["entry"]["options"]["username"] == "**REDACTED**"
    assert diag["coordinator"]["data"] == fake_coordinator.data
