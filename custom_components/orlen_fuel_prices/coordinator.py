"""Data update coordinator for the Ceny Paliw Orlen integration."""
from __future__ import annotations

import logging
from datetime import timedelta

from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from homeassistant.util import dt as dt_util

from .api import (
    OrlenApiClient,
    OrlenConnectionError,
    OrlenDataError,
    OrlenWafError,
)
from .const import (
    CONF_LPG_REGIONS,
    CONF_MARGIN,
    CONF_PRODUCTS,
    CONF_SCAN_INTERVAL,
    CONF_VAT_MODE,
    CONF_VAT_RATE,
    DEFAULT_LPG_REGIONS,
    DEFAULT_MARGIN,
    DEFAULT_PRODUCTS,
    DEFAULT_SCAN_INTERVAL,
    DEFAULT_VAT,
    NAME,
    VAT_MODE_AUTO,
    as_float,
)
from .pricing import compute_price, gross, vat_for, with_margin

_LOGGER = logging.getLogger(__name__)


class OrlenCoordinator(DataUpdateCoordinator[dict]):
    """Fetch and compute ORLEN fuel prices for all configured products."""

    def __init__(self, hass, api: OrlenApiClient, entry) -> None:
        options = {**entry.data, **entry.options}
        interval = int(
            as_float(options.get(CONF_SCAN_INTERVAL), DEFAULT_SCAN_INTERVAL)
        )
        super().__init__(
            hass,
            _LOGGER,
            name=NAME,
            update_interval=timedelta(seconds=max(interval, 60)),
        )
        self.api = api
        self.entry = entry

    @property
    def options(self) -> dict:
        return {**self.entry.data, **self.entry.options}

    async def _async_update_data(self) -> dict:
        options = self.options
        products = list(options.get(CONF_PRODUCTS) or DEFAULT_PRODUCTS)
        vat_mode = options.get(CONF_VAT_MODE, VAT_MODE_AUTO)
        vat_rate = as_float(options.get(CONF_VAT_RATE), DEFAULT_VAT)
        margin = as_float(options.get(CONF_MARGIN), DEFAULT_MARGIN)
        lpg_regions = list(options.get(CONF_LPG_REGIONS) or DEFAULT_LPG_REGIONS)

        try:
            motor_raw = await self.api.async_get_motor_prices()
            lpg_all = await self.api.async_get_lpg_prices() if lpg_regions else {}
            lpg_raw = {r: lpg_all[r] for r in lpg_regions if r in lpg_all}
        except OrlenWafError as err:
            raise UpdateFailed(f"ORLEN WAF rejected the request: {err}") from err
        except OrlenConnectionError as err:
            raise UpdateFailed(f"Cannot reach ORLEN API: {err}") from err
        except OrlenDataError as err:
            raise UpdateFailed(f"Invalid data from ORLEN API: {err}") from err

        motor: dict[str, dict] = {}
        for symbol in products:
            record = motor_raw.get(symbol)
            if record is None:
                _LOGGER.debug("Product %s not present in ORLEN snapshot", symbol)
                continue
            breakdown = compute_price(
                record.value_pln_per_m3,
                symbol,
                record.effective_date,
                vat_mode=vat_mode,
                vat_rate=vat_rate,
                margin=margin,
            )
            motor[symbol] = {
                **breakdown,
                "product": symbol,
                "effective_date": record.effective_date.isoformat(),
            }

        lpg: dict[str, dict] = {}
        for region, record in lpg_raw.items():
            override = vat_rate if vat_mode == "fixed" else None
            vat = vat_for("LPG", record.effective_date, override)
            brutto = gross(record.netto_pln_per_l, vat)
            lpg[region] = {
                "region": region,
                "product": "LPG",
                "effective_date": record.effective_date.isoformat(),
                "netto": record.netto_pln_per_l,
                "vat": vat,
                "brutto": brutto,
                "brutto_z_marza": with_margin(brutto, margin),
            }

        today = dt_util.utcnow().date()
        return {
            "motor": motor,
            "lpg": lpg,
            "margin": margin,
            "vat_mode": vat_mode,
            "vat_rate": vat_for(
                "Pb95", today, vat_rate if vat_mode == "fixed" else None
            ),
            "fetched_at": dt_util.utcnow().isoformat(),
        }
