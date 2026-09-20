"""Constants for the Ceny Paliw Orlen (ORLEN wholesale fuel prices) integration."""
from __future__ import annotations

DOMAIN = "orlen_fuel_prices"
NAME = "Ceny Paliw Orlen"

# Public, undocumented ORLEN "hurtowe ceny paliw" API. The WAF rejects requests
# without a browser-like User-Agent and the Referer of the public page.
BASE_URL = "https://tool.orlen.pl"
PAGE_URL = "https://www.orlen.pl/pl/dla-biznesu/hurtowe-ceny-paliw"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36",
    "Referer": PAGE_URL,
    "Accept": "application/json",
    "X-Requested-With": "XMLHttpRequest",
}

# Config entry data / options keys.
CONF_PRODUCTS = "products"
CONF_VAT_MODE = "vat_mode"
CONF_VAT_RATE = "vat_rate"
CONF_MARGIN = "margin"
CONF_SHOW_NETTO = "show_netto"
CONF_LPG_REGIONS = "lpg_regions"
CONF_SCAN_INTERVAL = "scan_interval"

VAT_MODE_AUTO = "auto"
VAT_MODE_FIXED = "fixed"

DEFAULT_VAT = 23  # %
DEFAULT_MARGIN = 0.0  # % — do not guess retail margin, default keeps it neutral
DEFAULT_SCAN_INTERVAL = 3600  # seconds (data changes at most once a day)
DEFAULT_SHOW_NETTO = True
DEFAULT_LPG_REGIONS: tuple[str, ...] = ()

MIN_SCAN_INTERVAL = 3600
MAX_SCAN_INTERVAL = 86400

REQUEST_TIMEOUT = 20

# Product catalog from /api/wholesalefuelprices/Products (symbol -> PL label).
PRODUCT_LABELS: dict[str, str] = {
    "Pb95": "Benzyna bezołowiowa Eurosuper 95",
    "Pb98": "Benzyna bezołowiowa Super Plus 98",
    "ONEkodiesel": "Olej napędowy Ekodiesel",
    "ONArctic2": "Olej napędowy Arktyczny 2",
    "ONSuper": "Olej napędowy Miejski Super",
    "OnEkoterm": "Olej napędowy grzewczy Ekoterm",
    "BIO100": "BIO 100",
}
PRODUCTS: tuple[str, ...] = tuple(PRODUCT_LABELS)
DEFAULT_PRODUCTS: tuple[str, ...] = (
    "Pb95",
    "Pb98",
    "ONEkodiesel",
    "ONArctic2",
    "OnEkoterm",
)

# Heating oils never qualified for the reduced VAT windows.
HEATING_PRODUCTS: frozenset[str] = frozenset(
    {"OnEkoterm", "HeatingC3", "HeatingC3LowSulfur"}
)

# Polish voivodeships as returned by /api/autogasprices (locationName).
LPG_REGIONS: tuple[str, ...] = (
    "dolnośląskie",
    "kujawsko-pomorskie",
    "lubelskie",
    "lubuskie",
    "łódzkie",
    "małopolskie",
    "mazowieckie",
    "opolskie",
    "podkarpackie",
    "podlaskie",
    "pomorskie",
    "śląskie",
    "świętokrzyskie",
    "warmińsko-mazurskie",
    "wielkopolskie",
    "zachodniopomorskie",
)

ATTR_PRODUCT = "product_symbol"
ATTR_EFFECTIVE_DATE = "effective_date"
ATTR_VAT_RATE = "vat_rate"
ATTR_MARGIN = "margin"
ATTR_STALE = "stale"
ATTR_SOURCE = "source"

SOURCE_URL = PAGE_URL


def as_float(value: object, default: float) -> float:
    """Coerce a config value to float, falling back to ``default``."""
    try:
        return float(value)  # type: ignore[arg-type]
    except (TypeError, ValueError):
        return default


def as_bool(value: object, default: bool = False) -> bool:
    """Coerce a config value to bool, falling back to ``default``."""
    if isinstance(value, bool):
        return value
    if value in (0, 1, "0", "1", "true", "false", "on", "off"):
        return str(value).lower() in ("1", "true", "on")
    return default
