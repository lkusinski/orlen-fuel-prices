"""Tests for the config and options flow."""
from __future__ import annotations

import pytest
from homeassistant.data_entry_flow import AbortFlow

from custom_components.orlen_fuel_prices.config_flow import (
    OrlenFuelPricesConfigFlow,
    OrlenFuelPricesOptionsFlow,
    build_schema,
)
from custom_components.orlen_fuel_prices.const import (
    CONF_LPG_REGIONS,
    CONF_MARGIN,
    CONF_PRODUCTS,
    CONF_SCAN_INTERVAL,
    CONF_SHOW_NETTO,
    CONF_VAT_MODE,
    CONF_VAT_RATE,
    DEFAULT_VAT,
    PRODUCT_LABELS,
    VAT_MODE_AUTO,
    VAT_MODE_FIXED,
)

VALID_INPUT = {
    CONF_PRODUCTS: ["Pb95", "ONEkodiesel"],
    CONF_VAT_MODE: VAT_MODE_AUTO,
    CONF_VAT_RATE: DEFAULT_VAT,
    CONF_MARGIN: 0,
    CONF_SHOW_NETTO: True,
    CONF_LPG_REGIONS: [],
    CONF_SCAN_INTERVAL: 3600,
}


def test_build_schema_defaults():
    result = build_schema({})({})
    assert result[CONF_VAT_MODE] == VAT_MODE_AUTO
    assert result[CONF_MARGIN] == 0
    assert result[CONF_SHOW_NETTO] is True
    assert result[CONF_SCAN_INTERVAL] == 3600


def test_build_schema_rejects_out_of_range_vat():
    import voluptuous as vol

    with pytest.raises(vol.Invalid):
        build_schema({})({**VALID_INPUT, CONF_VAT_RATE: 999})


async def test_step_user_shows_form():
    flow = OrlenFuelPricesConfigFlow()
    result = await flow.async_step_user(None)
    assert result["type"] == "form"
    assert result["step_id"] == "user"


async def test_step_user_creates_entry():
    flow = OrlenFuelPricesConfigFlow()
    result = await flow.async_step_user(VALID_INPUT)
    assert result["type"] == "create_entry"
    assert result["data"][CONF_VAT_MODE] == VAT_MODE_AUTO
    assert flow._unique_id is not None


async def test_step_user_preserves_product_selection():
    flow = OrlenFuelPricesConfigFlow()
    result = await flow.async_step_user({**VALID_INPUT, CONF_PRODUCTS: ["Pb98"]})
    assert result["data"][CONF_PRODUCTS] == {"Pb98": PRODUCT_LABELS["Pb98"]}


async def test_step_user_invalid_config_shows_error():
    flow = OrlenFuelPricesConfigFlow()
    result = await flow.async_step_user({**VALID_INPUT, CONF_SCAN_INTERVAL: 1})
    assert result["type"] == "form"
    assert result["errors"]["base"] == "invalid_config"


async def test_step_user_aborts_when_configured():
    flow = OrlenFuelPricesConfigFlow()
    flow._force_abort = True
    with pytest.raises(AbortFlow):
        await flow.async_step_user(VALID_INPUT)


async def test_options_flow_form_and_save():
    entry = type("Entry", (), {"data": {}, "options": {}})()
    flow = OrlenFuelPricesOptionsFlow(entry)
    assert (await flow.async_step_init(None))["type"] == "form"
    result = await flow.async_step_init(
        {**VALID_INPUT, CONF_MARGIN: 3.5, CONF_VAT_MODE: VAT_MODE_FIXED}
    )
    assert result["type"] == "create_entry"
    assert result["data"][CONF_MARGIN] == 3.5
    assert result["data"][CONF_VAT_MODE] == VAT_MODE_FIXED


async def test_options_flow_invalid_shows_error():
    entry = type("Entry", (), {"data": {}, "options": {}})()
    flow = OrlenFuelPricesOptionsFlow(entry)
    result = await flow.async_step_init({**VALID_INPUT, CONF_VAT_RATE: -5})
    assert result["type"] == "form"
    assert result["errors"]["base"] == "invalid_config"
