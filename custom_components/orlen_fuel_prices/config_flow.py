"""Config and options flow for the Ceny Paliw Orlen integration."""
from __future__ import annotations

import logging

import voluptuous as vol
from homeassistant import config_entries
from homeassistant.core import callback
from homeassistant.helpers import config_validation as cv

from .const import (
    CONF_LPG_REGIONS,
    CONF_MARGIN,
    CONF_PRODUCTS,
    CONF_SCAN_INTERVAL,
    CONF_SHOW_NETTO,
    CONF_VAT_MODE,
    CONF_VAT_RATE,
    DEFAULT_LPG_REGIONS,
    DEFAULT_MARGIN,
    DEFAULT_PRODUCTS,
    DEFAULT_SCAN_INTERVAL,
    DEFAULT_SHOW_NETTO,
    DEFAULT_VAT,
    DOMAIN,
    LPG_REGIONS,
    MAX_SCAN_INTERVAL,
    MIN_SCAN_INTERVAL,
    NAME,
    PRODUCT_LABELS,
    VAT_MODE_AUTO,
    VAT_MODE_FIXED,
)

_LOGGER = logging.getLogger(__name__)

VAT_MODE_OPTIONS = {
    VAT_MODE_AUTO: "automatyczny (tabela CPN 2026)",
    VAT_MODE_FIXED: "stały (wymuszony)",
}


def build_schema(defaults: dict | None = None) -> vol.Schema:
    """Build the shared schema for the config and options forms."""
    defaults = defaults or {}
    return vol.Schema(
        {
            vol.Required(
                CONF_PRODUCTS,
                default=defaults.get(CONF_PRODUCTS, list(DEFAULT_PRODUCTS)),
            ): cv.multi_select(PRODUCT_LABELS),
            vol.Required(
                CONF_VAT_MODE,
                default=defaults.get(CONF_VAT_MODE, VAT_MODE_AUTO),
            ): vol.In(VAT_MODE_OPTIONS),
            vol.Optional(
                CONF_VAT_RATE,
                default=defaults.get(CONF_VAT_RATE, DEFAULT_VAT),
            ): vol.All(vol.Coerce(float), vol.Range(min=0, max=100)),
            vol.Optional(
                CONF_MARGIN,
                default=defaults.get(CONF_MARGIN, DEFAULT_MARGIN),
            ): vol.All(vol.Coerce(float), vol.Range(min=0, max=1000)),
            vol.Optional(
                CONF_SHOW_NETTO,
                default=defaults.get(CONF_SHOW_NETTO, DEFAULT_SHOW_NETTO),
            ): cv.boolean,
            vol.Optional(
                CONF_LPG_REGIONS,
                default=list(
                    defaults.get(CONF_LPG_REGIONS, DEFAULT_LPG_REGIONS)
                ),
            ): cv.multi_select({region: region for region in LPG_REGIONS}),
            vol.Optional(
                CONF_SCAN_INTERVAL,
                default=defaults.get(CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL),
            ): vol.All(
                vol.Coerce(int),
                vol.Range(min=MIN_SCAN_INTERVAL, max=MAX_SCAN_INTERVAL),
            ),
        }
    )


class OrlenFuelPricesConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Initial configuration. The API needs no credentials."""

    VERSION = 1

    async def async_step_user(self, user_input=None):
        errors: dict[str, str] = {}
        if user_input is not None:
            try:
                validated = build_schema({})(user_input)
            except vol.Invalid as err:
                _LOGGER.debug("Invalid config input: %s", err)
                errors["base"] = "invalid_config"
            else:
                await self.async_set_unique_id(DOMAIN)
                self._abort_if_unique_id_configured()
                return self.async_create_entry(title=NAME, data=validated)

        return self.async_show_form(
            step_id="user",
            data_schema=build_schema({}),
            errors=errors,
        )

    @staticmethod
    @callback
    def async_get_options_flow(config_entry) -> "OrlenFuelPricesOptionsFlow":
        return OrlenFuelPricesOptionsFlow(config_entry)


class OrlenFuelPricesOptionsFlow(config_entries.OptionsFlow):
    """Edit products, VAT, margin, LPG regions and polling interval."""

    def __init__(self, config_entry=None) -> None:
        self._config_entry = config_entry

    @property
    def _entry(self):
        return getattr(self, "config_entry", None) or self._config_entry

    def _current(self) -> dict:
        entry = self._entry
        if entry is None:
            return {}
        return {**entry.data, **entry.options}

    async def async_step_init(self, user_input=None):
        errors: dict[str, str] = {}
        current = self._current()
        if user_input is not None:
            try:
                validated = build_schema(current)(user_input)
            except vol.Invalid as err:
                _LOGGER.debug("Invalid options input: %s", err)
                errors["base"] = "invalid_config"
            else:
                return self.async_create_entry(title="", data=validated)

        return self.async_show_form(
            step_id="init",
            data_schema=build_schema(current),
            errors=errors,
        )
