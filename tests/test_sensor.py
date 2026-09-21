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
    entry = _entry(options={CONF_PRODUCTS: ["Pb95"], CONF_SHOW_NETTO: True})
    entities = await _collect(fake_coordinator, entry)
    ids = {e.unique_id for e in entities}
    assert f"{DOMAIN}_Pb95_cena_netto" in ids
    assert f"{DOMAIN}_Pb95_cena_brutto" in ids
    assert f"{DOMAIN}_Pb95_cena_brutto_z_marza" in ids
    assert f"{DOMAIN}_Pb95_data_ceny" in ids
    assert f"{DOMAIN}_vat_rate" in ids
    # Margin is a number entity, not a sensor.
    assert f"{DOMAIN}_marza" not in ids


async def test_setup_skips_netto_when_disabled(fake_coordinator):
    entry = _entry(options={CONF_PRODUCTS: ["Pb95"], CONF_SHOW_NETTO: False})
    ids = {e.unique_id for e in await _collect(fake_coordinator, entry)}
    assert f"{DOMAIN}_Pb95_cena_netto" not in ids
    assert f"{DOMAIN}_Pb95_cena_brutto" in ids


async def test_setup_adds_lpg_entities(fake_coordinator):
    entry = _entry(
        options={
            CONF_PRODUCTS: ["Pb95"],
            CONF_LPG_REGIONS: ["mazowieckie"],
        }
    )
    ids = {e.unique_id for e in await _collect(fake_coordinator, entry)}
    assert f"{DOMAIN}_lpg_mazowieckie_cena_brutto_z_marza" in ids


def test_motor_sensor_values_and_attributes(fake_coordinator):
    sensor = OrlenMotorPriceSensor(fake_coordinator, "e1", "Pb95", "brutto")
    assert sensor.native_value == 7.803
    assert sensor.name == "Pb95 – cena brutto"
    assert sensor.unique_id == f"{DOMAIN}_Pb95_cena_brutto"
    attrs = sensor.extra_state_attributes
    assert attrs[ATTR_VAT_RATE] == 23.0
    assert attrs[ATTR_MARGIN] == 0.0


def test_motor_sensor_has_icon(fake_coordinator):
    sensor = OrlenMotorPriceSensor(fake_coordinator, "e1", "Pb95", "brutto")
    assert sensor._attr_icon == "mdi:cash"
    marza = OrlenMotorPriceSensor(fake_coordinator, "e1", "Pb95", "brutto_z_marza")
    assert marza._attr_icon == "mdi:cash-plus"


def test_vat_rate_sensor_value(fake_coordinator):
    assert OrlenVatRateSensor(fake_coordinator, "e1").native_value == 23.0


def test_date_sensor_value(fake_coordinator):
    sensor = OrlenMotorDateSensor(fake_coordinator, "e1", "Pb95")
    assert sensor.native_value == datetime(2026, 9, 19, tzinfo=timezone.utc)
    assert sensor.name == "Pb95 – data ceny"


def test_lpg_sensor_value(fake_coordinator):
    sensor = OrlenLpgPriceSensor(fake_coordinator, "e1", "mazowieckie", "brutto")
    assert sensor.native_value == 3.296


def test_sensor_unavailable_when_product_missing(fake_coordinator):
    sensor = OrlenMotorPriceSensor(fake_coordinator, "e1", "Pb98", "brutto")
    assert sensor.available is False
    assert sensor.native_value is None
