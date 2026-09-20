"""Pure pricing domain logic: netto -> brutto -> brutto z marżą.

No Home Assistant imports here on purpose, so it can be unit tested without the
full HA stack.
"""
from __future__ import annotations

from datetime import date

from .const import DEFAULT_MARGIN, DEFAULT_VAT, HEATING_PRODUCTS

# Reduced VAT windows (program CPN 2026), half-open ranges [start, end).
# Only motor fuels qualified; heating oils stayed at 23%.
REDUCED_VAT: tuple[tuple[date, date, int], ...] = (
    (date(2026, 3, 31), date(2026, 7, 1), 8),  # through 2026-06-30
    (date(2026, 8, 17), date(2026, 9, 1), 8),  # through 2026-08-31
)


def vat_for(
    product: str,
    day: date,
    override: float | None = None,
) -> float:
    """Return the VAT rate (%) for a product effective on ``day``.

    ``override`` (fixed-rate mode) always wins. Heating oils never receive the
    reduced rate.
    """
    if override is not None:
        return float(override)
    if product in HEATING_PRODUCTS:
        return float(DEFAULT_VAT)
    for start, end, rate in REDUCED_VAT:
        if start <= day < end:
            return float(rate)
    return float(DEFAULT_VAT)


def netto_from_value(value_pln_per_m3: float) -> float:
    """Convert the API ``value`` (PLN per 1000 l) to netto PLN/l (3 decimals)."""
    return round(float(value_pln_per_m3) / 1000.0, 3)


def gross(netto: float, vat: float) -> float:
    """Brutto PLN/l for a netto price and a VAT rate (%)."""
    return round(float(netto) * (1.0 + float(vat) / 100.0), 3)


def with_margin(price: float, margin: float) -> float:
    """Apply a margin (%) on top of a price. A 0% margin returns the price as-is."""
    return round(float(price) * (1.0 + float(margin) / 100.0), 3)


def compute_price(
    value_pln_per_m3: float,
    product: str,
    day: date,
    *,
    vat_mode: str = "auto",
    vat_rate: float | None = None,
    margin: float = DEFAULT_MARGIN,
) -> dict[str, float]:
    """Full price breakdown for one API record.

    Returns a dict with ``netto``, ``vat``, ``brutto`` and ``brutto_z_marza``.
    The margin defaults to 0%, where ``brutto_z_marza == brutto``.
    """
    override = vat_rate if vat_mode == "fixed" else None
    vat = vat_for(product, day, override)
    netto = netto_from_value(value_pln_per_m3)
    brutto = gross(netto, vat)
    return {
        "netto": netto,
        "vat": vat,
        "brutto": brutto,
        "brutto_z_marza": with_margin(brutto, margin),
    }
