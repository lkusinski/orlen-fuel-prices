"""Async client for the public ORLEN wholesale fuel prices API.

The API is unofficial and sits behind a WAF: requests without a browser-like
``User-Agent``/``Referer`` return HTTP 200 with an HTML ``Request Rejected``
body, which we surface as :class:`OrlenWafError` instead of parsing it as JSON.
"""
from __future__ import annotations

import asyncio
import json
import logging
from dataclasses import dataclass
from datetime import date

import aiohttp

from .const import BASE_URL, HEADERS, REQUEST_TIMEOUT

_LOGGER = logging.getLogger(__name__)


class OrlenApiError(Exception):
    """Base error for ORLEN API failures."""


class OrlenConnectionError(OrlenApiError):
    """Network/timeout/5xx failure."""


class OrlenWafError(OrlenApiError):
    """The WAF rejected the request (HTML instead of JSON)."""


class OrlenDataError(OrlenApiError):
    """Malformed or unparsable payload."""


@dataclass(frozen=True)
class MotorPrice:
    """A motor fuel price, as published in PLN per 1000 l (m3)."""

    product: str
    effective_date: date
    value_pln_per_m3: float


@dataclass(frozen=True)
class LpgPrice:
    """An autogas price, as published per region (already PLN/l)."""

    region: str
    effective_date: date
    netto_pln_per_l: float


def _looks_like_waf(raw: bytes, content_type: str = "") -> bool:
    if content_type and content_type.split(";", 1)[0].strip().lower() == "text/html":
        return True
    head = raw[:200].lstrip().lower()
    return head.startswith(b"<") or b"request rejected" in head


def _parse_effective_date(value: object) -> date:
    return date.fromisoformat(str(value)[:10])


def parse_motor_prices(data: object) -> list[MotorPrice]:
    """Parse a ``/api/wholesalefuelprices/`` payload."""
    if not isinstance(data, list):
        raise OrlenDataError(f"expected list, got {type(data).__name__}")
    out: list[MotorPrice] = []
    for row in data:
        if not isinstance(row, dict):
            raise OrlenDataError(f"bad record: {row!r}")
        try:
            out.append(
                MotorPrice(
                    product=str(row["productName"]),
                    effective_date=_parse_effective_date(row["effectiveDate"]),
                    value_pln_per_m3=float(row["value"]),
                )
            )
        except (KeyError, TypeError, ValueError) as err:
            raise OrlenDataError(f"bad record: {row!r}") from err
    return out


def parse_lpg_prices(data: object) -> list[LpgPrice]:
    """Parse an ``/api/autogasprices`` payload."""
    if not isinstance(data, list):
        raise OrlenDataError(f"expected list, got {type(data).__name__}")
    out: list[LpgPrice] = []
    for row in data:
        if not isinstance(row, dict):
            raise OrlenDataError(f"bad record: {row!r}")
        try:
            out.append(
                LpgPrice(
                    region=str(row["locationName"]),
                    effective_date=_parse_effective_date(row["effectiveDate"]),
                    # LPG ``value`` is already PLN/l (unit is null in the API).
                    netto_pln_per_l=round(float(row["value"]), 3),
                )
            )
        except (KeyError, TypeError, ValueError) as err:
            raise OrlenDataError(f"bad record: {row!r}") from err
    return out


class OrlenApiClient:
    """Thin async wrapper around the ORLEN endpoints."""

    def __init__(self, session: aiohttp.ClientSession, timeout: int = REQUEST_TIMEOUT) -> None:
        self._session = session
        self._timeout = timeout

    async def _async_get_json(self, path: str, params: dict | None = None) -> object:
        url = f"{BASE_URL}{path}"
        try:
            async with asyncio.timeout(self._timeout):
                async with self._session.get(url, headers=HEADERS, params=params) as resp:
                    raw = await resp.read()
                    status = resp.status
                    content_type = resp.headers.get("Content-Type", "")
        except (aiohttp.ClientError, TimeoutError) as err:
            raise OrlenConnectionError(f"request failed for {path}: {err}") from err

        if _looks_like_waf(raw, content_type):
            raise OrlenWafError(f"WAF rejected request to {path} (HTML instead of JSON)")
        if status in (401, 403):
            raise OrlenWafError(f"access denied ({status}) for {path}")
        if status >= 500:
            raise OrlenConnectionError(f"server error ({status}) for {path}")
        if status != 200:
            raise OrlenApiError(f"unexpected status {status} for {path}")

        try:
            return json.loads(raw.decode("utf-8-sig"))
        except (UnicodeDecodeError, json.JSONDecodeError) as err:
            raise OrlenDataError(f"invalid JSON from {path}") from err

    async def async_get_motor_prices(self) -> dict[str, MotorPrice]:
        """Current motor fuel prices keyed by product symbol."""
        data = await self._async_get_json("/api/wholesalefuelprices/")
        return {p.product: p for p in parse_motor_prices(data)}

    async def async_get_lpg_prices(self) -> dict[str, LpgPrice]:
        """Current autogas prices keyed by voivodeship."""
        data = await self._async_get_json("/api/autogasprices")
        return {p.region: p for p in parse_lpg_prices(data)}
