"""Shared test fixtures.

We mock the Home Assistant modules that the integration imports so the code
can be exercised without installing Home Assistant itself.
"""
from __future__ import annotations

import datetime as _dt
import sys
import types
from unittest.mock import AsyncMock, MagicMock

import voluptuous as vol


# --- minimal real cv helpers (mirrors the subset we use) -------------------
def _multi_select(options):
    # Mirrors homeassistant.helpers.config_validation.multi_select: it accepts
    # only a list of selected keys and returns a mapping key -> option label.
    options = options if isinstance(options, dict) else {o: o for o in options}

    def validator(value):
        if value is None:
            return {}
        if not isinstance(value, list):
            raise vol.Invalid("Not a list")
        return {key: options[key] for key in value if key in options}

    return validator


def _boolean(value):
    if isinstance(value, bool):
        return value
    if value in (1, "1", "true", "True", "on", "yes"):
        return True
    if value in (0, "0", "false", "False", "off", "no"):
        return False
    raise vol.Invalid(f"invalid boolean: {value!r}")


def _string(value):
    return str(value)


def _ensure_list(value):
    if value is None:
        return []
    if isinstance(value, (list, tuple, set)):
        return list(value)
    return [value]


# --- module mocks ----------------------------------------------------------
_HA_MODULES = [
    "homeassistant",
    "homeassistant.core",
    "homeassistant.config_entries",
    "homeassistant.data_entry_flow",
    "homeassistant.helpers",
    "homeassistant.helpers.aiohttp_client",
    "homeassistant.helpers.config_validation",
    "homeassistant.helpers.device_registry",
    "homeassistant.helpers.entity",
    "homeassistant.helpers.entity_platform",
    "homeassistant.helpers.update_coordinator",
    "homeassistant.components",
    "homeassistant.components.sensor",
    "homeassistant.const",
    "homeassistant.util",
]

for _mod_name in _HA_MODULES:
    if _mod_name not in sys.modules:
        sys.modules[_mod_name] = MagicMock()

# dt must be real, otherwise coordinator date math breaks under mocks.
_dt_mod = types.ModuleType("homeassistant.util.dt")
_dt_mod.utcnow = lambda: _dt.datetime.now(_dt.timezone.utc)
_dt_mod.parse_datetime = lambda value: _dt.datetime.fromisoformat(str(value))
sys.modules["homeassistant.util.dt"] = _dt_mod
sys.modules["homeassistant.util"].dt = _dt_mod

# config_validation
_cv = sys.modules["homeassistant.helpers.config_validation"]
_cv.multi_select = _multi_select
_cv.boolean = _boolean
_cv.string = _string
_cv.ensure_list = _ensure_list

# core
_core = sys.modules["homeassistant.core"]
_core.callback = lambda func: func
_core.HomeAssistant = object
_core.ServiceCall = object


class _SupportsResponse:
    NONE = "none"
    OPTIONAL = "optional"
    ONLY = "only"


_core.SupportsResponse = _SupportsResponse

# const
_const = sys.modules["homeassistant.const"]
_const.PERCENTAGE = "%"


class _Platform:
    SENSOR = "sensor"


class _EntityCategory:
    CONFIG = "config"
    DIAGNOSTIC = "diagnostic"


_const.Platform = _Platform
_const.EntityCategory = _EntityCategory

# data_entry_flow.AbortFlow as a real exception
class _AbortFlow(Exception):
    def __init__(self, reason: str = "") -> None:
        self.reason = reason
        super().__init__(reason)


sys.modules["homeassistant.data_entry_flow"].AbortFlow = _AbortFlow

# config_entries
_ce = sys.modules["homeassistant.config_entries"]


class _ConfigEntry:
    def __init__(self, *, data=None, options=None, entry_id="test-entry", title="ORLEN"):
        self.data = data or {}
        self.options = options or {}
        self.entry_id = entry_id
        self.title = title

    def async_on_unload(self, func):
        return func

    def add_update_listener(self, func):
        return func


class _ConfigFlow:
    def __init_subclass__(cls, **kwargs):
        pass

    def __init__(self):
        self.hass = MagicMock()
        self.context = {}
        self._unique_id = None
        self._force_abort = False

    async def async_set_unique_id(self, unique_id, *, raise_on_progress=True):
        self._unique_id = unique_id

    def _abort_if_unique_id_configured(self, updates=None, reload_on_update=True):
        if self._force_abort:
            raise _AbortFlow("already_configured")

    def async_show_form(
        self,
        *,
        step_id,
        data_schema=None,
        errors=None,
        description_placeholders=None,
    ):
        return {
            "type": "form",
            "step_id": step_id,
            "data_schema": data_schema,
            "errors": errors or {},
        }

    def async_create_entry(self, *, title, data, options=None):
        return {
            "type": "create_entry",
            "title": title,
            "data": data,
            "options": options or {},
        }


class _OptionsFlow:
    def __init_subclass__(cls, **kwargs):
        pass

    def __init__(self):
        self.hass = MagicMock()
        self.config_entry = None

    def async_show_form(
        self,
        *,
        step_id,
        data_schema=None,
        errors=None,
        description_placeholders=None,
    ):
        return {
            "type": "form",
            "step_id": step_id,
            "data_schema": data_schema,
            "errors": errors or {},
        }

    def async_create_entry(self, *, title, data, options=None):
        return {
            "type": "create_entry",
            "title": title,
            "data": data,
            "options": options or {},
        }


_ce.ConfigEntry = _ConfigEntry
_ce.ConfigFlow = _ConfigFlow
_ce.OptionsFlow = _OptionsFlow

# components.sensor
_sensor = sys.modules["homeassistant.components.sensor"]


class _SensorDeviceClass:
    MONETARY = "monetary"
    TIMESTAMP = "timestamp"
    ENUM = "enum"


class _SensorStateClass:
    MEASUREMENT = "measurement"
    TOTAL = "total"


class _SensorEntity:
    _attr_extra_state_attributes = {}

    @property
    def unique_id(self):
        return getattr(self, "_attr_unique_id", None)

    @property
    def name(self):
        return getattr(self, "_attr_name", None)


_sensor.SensorDeviceClass = _SensorDeviceClass
_sensor.SensorStateClass = _SensorStateClass
_sensor.SensorEntity = _SensorEntity

# helpers.device_registry.DeviceInfo
_gd = sys.modules["homeassistant.helpers.device_registry"]
_gd.DeviceInfo = lambda **kwargs: dict(kwargs)

# helpers.entity_platform
sys.modules["homeassistant.helpers.entity_platform"].AddEntitiesCallback = object

# helpers.update_coordinator
_uc = sys.modules["homeassistant.helpers.update_coordinator"]


class _CoordinatorEntity:
    def __init__(self, coordinator):
        self.coordinator = coordinator


class _DataUpdateCoordinator:
    def __class_getitem__(cls, item):
        return cls

    def __init__(self, hass, logger, *, name=None, update_interval=None):
        self.hass = hass
        self.logger = logger
        self.name = name
        self.update_interval = update_interval
        self.data = None
        self.last_update_success = True

    async def async_config_entry_first_refresh(self):
        self.data = await self._async_update_data()
        self.last_update_success = True


_uc.CoordinatorEntity = _CoordinatorEntity
_uc.DataUpdateCoordinator = _DataUpdateCoordinator
_uc.UpdateFailed = Exception

# helpers.aiohttp_client
sys.modules["homeassistant.helpers.aiohttp_client"].async_get_clientsession = (
    lambda hass: MagicMock()
)

# Because the parent packages are MagicMock instances, `from a.b import c`
# would return a fresh child mock instead of the module/attribute we configured.
# Pin every attribute we import on its parent package explicitly.
_ha = sys.modules["homeassistant"]
_ha.core = _core
_ha.const = _const
_ha.config_entries = _ce
_ha.data_entry_flow = sys.modules["homeassistant.data_entry_flow"]

_helpers = sys.modules["homeassistant.helpers"]
_helpers.aiohttp_client = sys.modules["homeassistant.helpers.aiohttp_client"]
_helpers.config_validation = _cv
_helpers.device_registry = _gd
_helpers.entity_platform = sys.modules["homeassistant.helpers.entity_platform"]
_helpers.update_coordinator = _uc
_helpers.entity = sys.modules["homeassistant.helpers.entity"]

_components = sys.modules["homeassistant.components"]
_components.sensor = _sensor

_util = sys.modules["homeassistant.util"]
_util.dt = _dt_mod

# Now it is safe to import integration code.
import aiohttp  # noqa: E402
import pytest  # noqa: E402

from custom_components.orlen_fuel_prices.api import OrlenApiClient  # noqa: E402


@pytest.fixture
def mock_session():
    session = MagicMock(spec=aiohttp.ClientSession)
    session.closed = False
    return session


@pytest.fixture
def api(mock_session):
    return OrlenApiClient(mock_session)


@pytest.fixture
def motor_payload():
    return {
        "motor": {
            "Pb95": {
                "product": "Pb95",
                "effective_date": "2026-09-19",
                "netto": 6.344,
                "vat": 23.0,
                "brutto": 7.803,
                "brutto_z_marza": 7.803,
            },
            "ONArctic2": {
                "product": "ONArctic2",
                "effective_date": "2026-09-19",
                "netto": 7.997,
                "vat": 23.0,
                "brutto": 9.836,
                "brutto_z_marza": 9.836,
            },
        },
        "lpg": {
            "mazowieckie": {
                "region": "mazowieckie",
                "product": "LPG",
                "effective_date": "2026-09-18",
                "netto": 2.68,
                "vat": 23.0,
                "brutto": 3.296,
                "brutto_z_marza": 3.296,
            },
        },
        "margin": 0.0,
        "vat_mode": "auto",
        "vat_rate": 23.0,
        "fetched_at": "2026-09-20T10:00:00+00:00",
    }


class _FakeCoordinator:
    def __init__(self, data):
        self.data = data
        self.last_update_success = True


@pytest.fixture
def fake_coordinator(motor_payload):
    return _FakeCoordinator(motor_payload)


@pytest.fixture
def response_factory():
    return make_mock_response


def make_mock_response(status=200, json_data=None, content_type="application/json", body=None):
    """Build an async context manager mimicking ``session.get(...)``."""
    import json as _json

    if body is None:
        body = _json.dumps(json_data if json_data is not None else {}).encode()

    response = MagicMock()
    response.status = status
    response.headers = {"Content-Type": content_type}
    response.read = AsyncMock(return_value=body)

    ctx = MagicMock()
    ctx.__aenter__ = AsyncMock(return_value=response)
    ctx.__aexit__ = AsyncMock(return_value=False)
    return ctx
