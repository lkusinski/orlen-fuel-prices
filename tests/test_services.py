"""Tests for the get_prices service."""
from __future__ import annotations

import pytest

from custom_components.orlen_fuel_prices.const import DOMAIN
from custom_components.orlen_fuel_prices.services import _async_handle_get_prices


class _Call:
    def __init__(self, hass, data=None):
        self.hass = hass
        self.data = data or {}


async def test_get_prices_returns_response(fake_coordinator):
    hass = type("Hass", (), {})()
    hass.data = {DOMAIN: {"e1": {"coordinator": fake_coordinator}}}
    result = await _async_handle_get_prices(_Call(hass))
    assert result["motor"]["Pb95"]["brutto"] == 7.803
    assert result["margin"] == 0.0
    assert result["vat_rate"] == 23.0


async def test_get_prices_entry_id(fake_coordinator):
    hass = type("Hass", (), {})()
    hass.data = {DOMAIN: {"e1": {"coordinator": fake_coordinator}}}
    result = await _async_handle_get_prices(_Call(hass, {"entry_id": "e1"}))
    assert "motor" in result


async def test_get_prices_unknown_entry_id(fake_coordinator):
    import voluptuous as vol

    hass = type("Hass", (), {})()
    hass.data = {DOMAIN: {"e1": {"coordinator": fake_coordinator}}}
    with pytest.raises(vol.Invalid):
        await _async_handle_get_prices(_Call(hass, {"entry_id": "nope"}))
