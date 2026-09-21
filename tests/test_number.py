"""Tests for the margin number platform."""
from __future__ import annotations

from unittest.mock import MagicMock

from custom_components.orlen_fuel_prices.const import CONF_MARGIN, DOMAIN
from custom_components.orlen_fuel_prices.number import (
    OrlenMarginNumber,
    async_setup_entry,
)


class _Entry:
    entry_id = "e1"
    title = "Ceny Paliw Orlen"
    data: dict = {}
    options: dict = {}


def _coordinator(margin=0.0, entry=None):
    return type(
        "Coordinator",
        (),
        {"data": {"margin": margin}, "entry": entry or _Entry()},
    )()


async def test_setup_adds_margin_number():
    coord = _coordinator()
    hass = type("Hass", (), {})()
    hass.data = {DOMAIN: {"e1": {"coordinator": coord}}}
    captured = []
    await async_setup_entry(hass, _Entry(), lambda e: captured.extend(e))
    assert len(captured) == 1
    assert captured[0].unique_id == f"{DOMAIN}_marza"
    assert captured[0].name == "Marża"


def test_native_value_reads_margin():
    number = OrlenMarginNumber(_coordinator(margin=7.5), "e1")
    assert number.native_value == 7.5
    assert number._attr_native_min_value == 0
    assert number._attr_native_step == 0.1


async def test_set_native_value_persists_to_options():
    entry = _Entry()
    entry.options = {"products": ["Pb95"]}
    hass = MagicMock()
    coord = _coordinator(entry=entry)
    number = OrlenMarginNumber(coord, "e1")
    number.hass = hass
    await number.async_set_native_value(5.0)
    hass.config_entries.async_update_entry.assert_called_once()
    kwargs = hass.config_entries.async_update_entry.call_args.kwargs
    assert kwargs["options"][CONF_MARGIN] == 5.0
    assert kwargs["options"]["products"] == ["Pb95"]
