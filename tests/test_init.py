"""Tests for integration setup, unload and services registration."""
from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

from custom_components.orlen_fuel_prices import (
    async_setup,
    async_setup_entry,
    async_unload_entry,
)
from custom_components.orlen_fuel_prices.const import DOMAIN


class _Entry:
    entry_id = "e1"
    title = "Ceny Paliw Orlen"
    data = {}
    options = {"products": ["Pb95"], "show_netto": True}

    def async_on_unload(self, func):
        return func

    def add_update_listener(self, func):
        return func


class _Hass:
    def __init__(self):
        self.data = {}
        self.services = MagicMock()
        self.services.has_service = MagicMock(return_value=False)
        self.config_entries = MagicMock()
        self.config_entries.async_forward_entry_setups = AsyncMock()
        self.config_entries.async_unload_platforms = AsyncMock(return_value=True)
        self.config_entries.async_reload = AsyncMock()


def _patched_client():
    client_cls = MagicMock()
    client_cls.return_value.async_get_motor_prices = AsyncMock(return_value={})
    client_cls.return_value.async_get_lpg_prices = AsyncMock(return_value={})
    return client_cls


async def test_async_setup_registers_services():
    hass = _Hass()
    with patch(
        "custom_components.orlen_fuel_prices.async_setup_services", new=AsyncMock()
    ) as setup_services:
        assert await async_setup(hass, {}) is True
        setup_services.assert_awaited_once_with(hass)


async def test_async_setup_entry_stores_coordinator():
    hass = _Hass()
    entry = _Entry()
    with patch(
        "custom_components.orlen_fuel_prices.OrlenApiClient", _patched_client()
    ):
        assert await async_setup_entry(hass, entry) is True
    assert entry.entry_id in hass.data[DOMAIN]
    assert "coordinator" in hass.data[DOMAIN][entry.entry_id]
    hass.config_entries.async_forward_entry_setups.assert_awaited_once()


async def test_async_unload_entry_cleans_up():
    hass = _Hass()
    entry = _Entry()
    with patch(
        "custom_components.orlen_fuel_prices.OrlenApiClient", _patched_client()
    ):
        await async_setup_entry(hass, entry)
    assert await async_unload_entry(hass, entry) is True
    assert entry.entry_id not in hass.data[DOMAIN]
