"""Sensor platform for the Ceny Paliw Orlen integration."""
from __future__ import annotations

from datetime import datetime, timezone

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import PERCENTAGE, EntityCategory
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import (
    ATTR_EFFECTIVE_DATE,
    ATTR_MARGIN,
    ATTR_PRODUCT,
    ATTR_SOURCE,
    ATTR_STALE,
    ATTR_VAT_RATE,
    CONF_LPG_REGIONS,
    CONF_PRODUCTS,
    CONF_SHOW_NETTO,
    DEFAULT_LPG_REGIONS,
    DEFAULT_PRODUCTS,
    DEFAULT_SHOW_NETTO,
    DOMAIN,
    PAGE_URL,
    PRODUCT_SHORT,
    SOURCE_URL,
    as_bool,
)

PRICE_UNIT = "zł/l"

# Display titles and icons per price kind.
PRICE_TITLES = {
    "netto": "cena netto",
    "brutto": "cena brutto",
    "brutto_z_marza": "cena z marżą",
}
PRICE_ICONS = {
    "netto": "mdi:cash-minus",
    "brutto": "mdi:cash",
    "brutto_z_marza": "mdi:cash-plus",
}
LPG_ICON = "mdi:gas-cylinder"


def _parse_dt(value: object) -> datetime | None:
    if not value:
        return None
    try:
        parsed = datetime.fromisoformat(str(value))
    except ValueError:
        return None
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed


def _device_info() -> DeviceInfo:
    return DeviceInfo(
        identifiers={(DOMAIN, "orlen")},
        name="ORLEN",
        manufacturer="ORLEN",
        model="Hurtowe ceny paliw",
        configuration_url=PAGE_URL,
    )


class OrlenBaseSensor(CoordinatorEntity, SensorEntity):
    """Shared behaviour: one ORLEN device and stale/version attributes."""

    _attr_has_entity_name = True
    _attr_should_poll = False

    def __init__(self, coordinator, entry_id: str) -> None:
        super().__init__(coordinator)
        self._entry_id = entry_id
        self._attr_device_info = _device_info()

    @property
    def available(self) -> bool:
        return self.coordinator.data is not None

    @property
    def _stale(self) -> bool:
        return not getattr(self.coordinator, "last_update_success", True)

    @property
    def extra_state_attributes(self) -> dict:
        attrs = dict(getattr(self, "_attr_extra_state_attributes", None) or {})
        attrs[ATTR_STALE] = self._stale
        attrs[ATTR_SOURCE] = SOURCE_URL
        return attrs


class OrlenMotorPriceSensor(OrlenBaseSensor):
    """Netto / brutto / brutto z marżą for a single motor fuel."""

    def __init__(self, coordinator, entry_id: str, product: str, price_key: str) -> None:
        super().__init__(coordinator, entry_id)
        self._product = product
        self._price_key = price_key
        short = PRODUCT_SHORT.get(product, product)
        self._attr_name = f"{short} – {PRICE_TITLES[price_key]}"
        self._attr_unique_id = f"{DOMAIN}_{product}_cena_{price_key}"
        self._attr_icon = PRICE_ICONS[price_key]
        self._attr_native_unit_of_measurement = PRICE_UNIT
        # No device_class MONETARY: with a measurement state_class HA warns about
        # the combination (see old package). A price in zł/l is a measurement.
        self._attr_state_class = SensorStateClass.MEASUREMENT
        self._attr_suggested_display_precision = 3

    @property
    def _record(self) -> dict | None:
        return (self.coordinator.data or {}).get("motor", {}).get(self._product)

    @property
    def available(self) -> bool:
        return self._record is not None

    @property
    def native_value(self) -> float | None:
        record = self._record
        return None if record is None else record.get(self._price_key)

    @property
    def extra_state_attributes(self) -> dict:
        attrs = super().extra_state_attributes
        record = self._record
        if record:
            attrs[ATTR_PRODUCT] = self._product
            attrs[ATTR_EFFECTIVE_DATE] = record.get("effective_date")
            attrs[ATTR_VAT_RATE] = record.get("vat")
            attrs[ATTR_MARGIN] = (self.coordinator.data or {}).get("margin")
        return attrs


class OrlenMotorDateSensor(OrlenBaseSensor):
    """Effective date of the published price for a motor fuel."""

    _attr_device_class = SensorDeviceClass.TIMESTAMP
    _attr_entity_category = EntityCategory.DIAGNOSTIC
    _attr_icon = "mdi:calendar-clock"

    def __init__(self, coordinator, entry_id: str, product: str) -> None:
        super().__init__(coordinator, entry_id)
        self._product = product
        short = PRODUCT_SHORT.get(product, product)
        self._attr_name = f"{short} – data ceny"
        self._attr_unique_id = f"{DOMAIN}_{product}_data_ceny"

    @property
    def _record(self) -> dict | None:
        return (self.coordinator.data or {}).get("motor", {}).get(self._product)

    @property
    def available(self) -> bool:
        return self._record is not None

    @property
    def native_value(self) -> datetime | None:
        record = self._record
        return None if record is None else _parse_dt(record.get("effective_date"))

    @property
    def extra_state_attributes(self) -> dict:
        attrs = super().extra_state_attributes
        attrs[ATTR_PRODUCT] = self._product
        return attrs


class OrlenLpgPriceSensor(OrlenBaseSensor):
    """Netto / brutto / brutto z marżą for autogas in one voivodeship."""

    _attr_icon = LPG_ICON

    def __init__(self, coordinator, entry_id: str, region: str, price_key: str) -> None:
        super().__init__(coordinator, entry_id)
        self._region = region
        self._price_key = price_key
        self._attr_name = f"LPG {region} – {PRICE_TITLES[price_key]}"
        self._attr_unique_id = f"{DOMAIN}_lpg_{region}_cena_{price_key}"
        self._attr_native_unit_of_measurement = PRICE_UNIT
        self._attr_state_class = SensorStateClass.MEASUREMENT
        self._attr_suggested_display_precision = 3

    @property
    def _record(self) -> dict | None:
        return (self.coordinator.data or {}).get("lpg", {}).get(self._region)

    @property
    def available(self) -> bool:
        return self._record is not None

    @property
    def native_value(self) -> float | None:
        record = self._record
        return None if record is None else record.get(self._price_key)

    @property
    def extra_state_attributes(self) -> dict:
        attrs = super().extra_state_attributes
        record = self._record
        if record:
            attrs[ATTR_PRODUCT] = "LPG"
            attrs[ATTR_EFFECTIVE_DATE] = record.get("effective_date")
            attrs[ATTR_VAT_RATE] = record.get("vat")
            attrs[ATTR_MARGIN] = (self.coordinator.data or {}).get("margin")
        return attrs


class OrlenVatRateSensor(OrlenBaseSensor):
    """Currently applied VAT rate for motor fuels."""

    _attr_native_unit_of_measurement = PERCENTAGE
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_entity_category = EntityCategory.DIAGNOSTIC
    _attr_icon = "mdi:percent"

    def __init__(self, coordinator, entry_id: str) -> None:
        super().__init__(coordinator, entry_id)
        self._attr_name = "Aktualna stawka VAT"
        self._attr_unique_id = f"{DOMAIN}_vat_rate"

    @property
    def native_value(self) -> float | None:
        return (self.coordinator.data or {}).get("vat_rate")


class OrlenLastUpdateSensor(OrlenBaseSensor):
    """Timestamp of the last successful data fetch."""

    _attr_device_class = SensorDeviceClass.TIMESTAMP
    _attr_entity_category = EntityCategory.DIAGNOSTIC
    _attr_icon = "mdi:clock-check-outline"

    def __init__(self, coordinator, entry_id: str) -> None:
        super().__init__(coordinator, entry_id)
        self._attr_name = "Ostatnia aktualizacja"
        self._attr_unique_id = f"{DOMAIN}_last_update"

    @property
    def native_value(self) -> datetime | None:
        return _parse_dt((self.coordinator.data or {}).get("fetched_at"))


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the sensors from the current coordinator data."""
    coordinator = hass.data[DOMAIN][entry.entry_id]["coordinator"]
    options = {**entry.data, **entry.options}

    products = list(options.get(CONF_PRODUCTS) or DEFAULT_PRODUCTS)
    show_netto = as_bool(options.get(CONF_SHOW_NETTO), DEFAULT_SHOW_NETTO)
    lpg_regions = list(options.get(CONF_LPG_REGIONS) or DEFAULT_LPG_REGIONS)

    entities: list[SensorEntity] = []
    for product in products:
        if show_netto:
            entities.append(
                OrlenMotorPriceSensor(coordinator, entry.entry_id, product, "netto")
            )
        entities.append(
            OrlenMotorPriceSensor(coordinator, entry.entry_id, product, "brutto")
        )
        entities.append(
            OrlenMotorPriceSensor(
                coordinator, entry.entry_id, product, "brutto_z_marza"
            )
        )
        entities.append(OrlenMotorDateSensor(coordinator, entry.entry_id, product))

    for region in lpg_regions:
        for price_key in ("netto", "brutto", "brutto_z_marza"):
            entities.append(
                OrlenLpgPriceSensor(coordinator, entry.entry_id, region, price_key)
            )

    entities.extend(
        [
            OrlenVatRateSensor(coordinator, entry.entry_id),
            OrlenLastUpdateSensor(coordinator, entry.entry_id),
        ]
    )

    async_add_entities(entities)
