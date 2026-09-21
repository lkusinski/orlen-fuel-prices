"""Number platform for the Ceny Paliw Orlen integration.

Exposes the margin as a UI-editable entity so it can be changed without opening
the options flow. The value is stored in the config entry options and the entry
is reloaded so every sensor picks up the new margin.
"""
from __future__ import annotations

from homeassistant.components.number import NumberEntity, NumberMode
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import PERCENTAGE, EntityCategory
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import CONF_MARGIN, DEFAULT_MARGIN, DOMAIN, PAGE_URL


class OrlenMarginNumber(CoordinatorEntity, NumberEntity):
    """Margin (%) added on top of the brutto price."""

    _attr_has_entity_name = True
    _attr_should_poll = False
    _attr_name = "Marża"
    _attr_icon = "mdi:percent-box"
    _attr_native_unit_of_measurement = PERCENTAGE
    _attr_native_min_value = 0
    _attr_native_max_value = 1000
    _attr_native_step = 0.1
    _attr_mode = NumberMode.BOX
    _attr_entity_category = EntityCategory.CONFIG

    def __init__(self, coordinator, entry_id: str) -> None:
        super().__init__(coordinator)
        self._entry_id = entry_id
        self._attr_unique_id = f"{DOMAIN}_marza"
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, "orlen")},
            name="ORLEN",
            manufacturer="ORLEN",
            model="Hurtowe ceny paliw",
            configuration_url=PAGE_URL,
        )

    @property
    def available(self) -> bool:
        return self.coordinator.data is not None

    @property
    def native_value(self) -> float:
        return (self.coordinator.data or {}).get("margin", DEFAULT_MARGIN)

    async def async_set_native_value(self, value: float) -> None:
        """Persist the new margin and reload the entry to recompute prices."""
        entry = getattr(self.coordinator, "entry", None)
        if entry is None:
            return
        options = {**entry.options, CONF_MARGIN: float(value)}
        self.hass.config_entries.async_update_entry(entry, options=options)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the margin number entity."""
    coordinator = hass.data[DOMAIN][entry.entry_id]["coordinator"]
    async_add_entities([OrlenMarginNumber(coordinator, entry.entry_id)])
