"""Tests for the sensor platform."""
from __future__ import annotations

from datetime import datetime, timezone

from custom_components.orlen_fuel_prices.const import (
    ATTR_MARGIN,
    ATTR_VAT_RATE,
    CONF_LPG_REGIONS,
    CONF_PRODUCTS,
    CONF_SHOW_NETTO,
    DOMAIN,
)
from custom_components.orlen_fuel_prices.sensor import (
    OrlenLpgPriceSensor,
    OrlenMarginSensor,
    OrlenMotorDateSensor,
    OrlenMotorPriceSensor,
    OrlenVatRateSensor,
    async_setup_entry,
)


def _entry(options=None, data=None):
    return type(
        "Entry",
        (),
        {"data": data or {}, "options": options or {}, "entry_id": "e1"},
    )()


async def _collect(coordinator, entry):
    hass = type("Hass", (), {})()
    hass.data = {DOMAIN: {entry.entry_id: {"coordinator": coordinator}}}
    captured = []

    def add(entities):
        captured.extend(entities)

    await async_setup_entry(hass, entry, add)
    return captured


async def test_setup_creates_expected_entities(fake_coordinator):
    entry = _entry(
        options={CONF_PRODUCTS: ["Pb95"], CONF_SHOW_NETTO: True}
    )
    entities = await _collect(fake_coordinator, entry)
    ids = {e.unique_id for e in entities}
    assert f"{DOMAIN}_Pb95_netto" in ids
    assert f"{DOMAIN}_Pb95_brutto" in ids
    assert f"{DOMAIN}_Pb95_brutto_z_marza" in ids
    assert f"{DOMAIN}_Pb95_effective_date" in ids
    assert f"{DOMAIN}_margin" in ids
    assert f"{DOMAIN}_vat_rate" in ids


async def test_setup_skips_netto_when_disabled(fake_coordinator):
    entry = _entry(
        options={CONF_PRODUCTS: ["Pb95"], CONF_SHOW_NETTO: False}
    )
    ids = {e.unique_id for e in await _collect(fake_coordinator, entry)}
    assert f"{DOMAIN}_Pb95_netto" not in ids
    assert f"{DOMAIN}_Pb95_brutto" in ids


async def test_setup_adds_lpg_entities(fake_coordinator):
    entry = _entry(
        options={
            CONF_PRODUCTS: ["Pb95"],
            CONF_LPG_REGIONS: ["mazowieckie"],
        }
    )
    ids = {e.unique_id for e in await _collect(fake_coordinator, entry)}
    assert f"{DOMAIN}_lpg_mazowieckie_brutto_z_marza" in ids


def test_motor_sensor_values_and_attributes(fake_coordinator):
    sensor = OrlenMotorPriceSensor(fake_coordinator, "e1", "Pb95", "brutto")
    assert sensor.native_value == 7.803
    attrs = sensor.extra_state_attributes
    assert attrs[ATTR_VAT_RATE] == 23.0
    assert attrs[ATTR_MARGIN] == 0.0


def test_margin_sensor_value(fake_coordinator):
    sensor = OrlenMarginSensor(fake_coordinator, "e1")
    assert sensor.native_value == 0.0


def test_margin_sensor_is_not_config_category(fake_coordinator):
    # Regression: HA refuses to add sensors with EntityCategory.CONFIG.
    sensor = OrlenMarginSensor(fake_coordinator, "e1")
    assert getattr(sensor, "_attr_entity_category", None) is None


def test_vat_rate_sensor_value(fake_coordinator):
    sensor = OrlenVatRateSensor(fake_coordinator, "e1")
    assert sensor.native_value == 23.0


def test_date_sensor_value(fake_coordinator):
    sensor = OrlenMotorDateSensor(fake_coordinator, "e1", "Pb95")
    assert sensor.native_value == datetime(2026, 9, 19, tzinfo=timezone.utc)


def test_lpg_sensor_value(fake_coordinator):
    sensor = OrlenLpgPriceSensor(fake_coordinator, "e1", "mazowieckie", "brutto")
    assert sensor.native_value == 3.296


def test_sensor_unavailable_when_product_missing(fake_coordinator):
    sensor = OrlenMotorPriceSensor(fake_coordinator, "e1", "Pb98", "brutto")
    assert sensor.available is False
    assert sensor.native_value is None
