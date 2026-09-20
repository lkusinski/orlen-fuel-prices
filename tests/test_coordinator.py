"""Tests for the data update coordinator."""
from __future__ import annotations

from datetime import date
from unittest.mock import AsyncMock, MagicMock

import pytest
from homeassistant.helpers.update_coordinator import UpdateFailed

from custom_components.orlen_fuel_prices.api import (
    LpgPrice,
    MotorPrice,
    OrlenWafError,
)
from custom_components.orlen_fuel_prices.const import (
    CONF_LPG_REGIONS,
    CONF_MARGIN,
    CONF_PRODUCTS,
    CONF_SCAN_INTERVAL,
    CONF_VAT_MODE,
    CONF_VAT_RATE,
    VAT_MODE_FIXED,
)
from custom_components.orlen_fuel_prices.coordinator import OrlenCoordinator


def _entry(data=None, options=None):
    return type(
        "Entry",
        (),
        {"data": data or {}, "options": options or {}, "entry_id": "e1"},
    )()


def _api(motor=None, lpg=None, error=None):
    api = MagicMock()
    if error is not None:
        api.async_get_motor_prices = AsyncMock(side_effect=error)
    else:
        api.async_get_motor_prices = AsyncMock(return_value=motor or {})
    api.async_get_lpg_prices = AsyncMock(return_value=lpg or {})
    return api


def _motor():
    return {
        "Pb95": MotorPrice("Pb95", date(2026, 9, 19), 6344.0),
        "ONArctic2": MotorPrice("ONArctic2", date(2026, 9, 19), 7997.0),
        "OnEkoterm": MotorPrice("OnEkoterm", date(2026, 4, 15), 6088.0),
    }


async def test_coordinator_computes_prices():
    entry = _entry(options={CONF_PRODUCTS: ["Pb95"], CONF_SCAN_INTERVAL: 3600})
    coordinator = OrlenCoordinator(MagicMock(), _api(motor=_motor()), entry)
    data = await coordinator._async_update_data()
    pb95 = data["motor"]["Pb95"]
    assert pb95["netto"] == 6.344
    assert pb95["brutto"] == 7.803
    assert pb95["brutto_z_marza"] == 7.803
    assert pb95["effective_date"] == "2026-09-19"


async def test_coordinator_margin_default_zero_no_change():
    entry = _entry(options={CONF_PRODUCTS: ["Pb95"], CONF_MARGIN: 0})
    coordinator = OrlenCoordinator(MagicMock(), _api(motor=_motor()), entry)
    data = await coordinator._async_update_data()
    assert data["motor"]["Pb95"]["brutto_z_marza"] == data["motor"]["Pb95"]["brutto"]
    assert data["margin"] == 0


async def test_coordinator_margin_included():
    entry = _entry(options={CONF_PRODUCTS: ["Pb95"], CONF_MARGIN: 5})
    coordinator = OrlenCoordinator(MagicMock(), _api(motor=_motor()), entry)
    data = await coordinator._async_update_data()
    assert data["motor"]["Pb95"]["brutto_z_marza"] == 8.193


async def test_coordinator_fixed_vat_mode():
    entry = _entry(
        options={
            CONF_PRODUCTS: ["OnEkoterm"],
            CONF_VAT_MODE: VAT_MODE_FIXED,
            CONF_VAT_RATE: 0,
        }
    )
    coordinator = OrlenCoordinator(MagicMock(), _api(motor=_motor()), entry)
    data = await coordinator._async_update_data()
    assert data["motor"]["OnEkoterm"]["vat"] == 0
    assert data["motor"]["OnEkoterm"]["netto"] == 6.088


async def test_coordinator_auto_vat_heating_stays_23():
    entry = _entry(options={CONF_PRODUCTS: ["OnEkoterm"]})
    coordinator = OrlenCoordinator(MagicMock(), _api(motor=_motor()), entry)
    data = await coordinator._async_update_data()
    assert data["motor"]["OnEkoterm"]["vat"] == 23


async def test_coordinator_lpg_only_selected_regions():
    lpg = {
        "mazowieckie": LpgPrice("mazowieckie", date(2026, 9, 18), 2.68),
        "śląskie": LpgPrice("śląskie", date(2026, 9, 18), 2.66),
    }
    entry = _entry(
        options={CONF_LPG_REGIONS: ["mazowieckie"], CONF_PRODUCTS: ["Pb95"]}
    )
    coordinator = OrlenCoordinator(MagicMock(), _api(motor=_motor(), lpg=lpg), entry)
    data = await coordinator._async_update_data()
    assert set(data["lpg"]) == {"mazowieckie"}
    assert data["lpg"]["mazowieckie"]["brutto"] == 3.296


async def test_coordinator_waf_raises_update_failed():
    entry = _entry(options={CONF_PRODUCTS: ["Pb95"]})
    coordinator = OrlenCoordinator(
        MagicMock(), _api(error=OrlenWafError("rejected")), entry
    )
    with pytest.raises(UpdateFailed):
        await coordinator._async_update_data()
