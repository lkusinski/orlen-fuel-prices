"""Tests for the ORLEN API client and parsers."""
from __future__ import annotations

import asyncio
from datetime import date
from unittest.mock import AsyncMock, MagicMock

import aiohttp
import pytest

from custom_components.orlen_fuel_prices.api import (
    LpgPrice,
    MotorPrice,
    OrlenApiClient,
    OrlenConnectionError,
    OrlenDataError,
    OrlenWafError,
    parse_lpg_prices,
    parse_motor_prices,
)

MOTOR_JSON = [
    {
        "productName": "Pb95",
        "effectiveDate": "2026-09-19T00:00:00",
        "value": 6344.0,
    },
    {
        "productName": "ONEkodiesel",
        "effectiveDate": "2026-09-19T00:00:00",
        "value": 7522.0,
    },
]

LPG_JSON = [
    {
        "effectiveDate": "2026-09-18T00:00:00",
        "locationName": "dolnośląskie",
        "value": 2.68,
        "productName": "LPG",
    }
]


def test_parse_motor_prices():
    prices = parse_motor_prices(MOTOR_JSON)
    assert prices[0] == MotorPrice("Pb95", date(2026, 9, 19), 6344.0)
    assert prices[1].product == "ONEkodiesel"


def test_parse_motor_prices_rejects_non_list():
    with pytest.raises(OrlenDataError):
        parse_motor_prices({"not": "a list"})


def test_parse_motor_prices_rejects_bad_record():
    with pytest.raises(OrlenDataError):
        parse_motor_prices([{"productName": "Pb95"}])


def test_parse_lpg_prices():
    prices = parse_lpg_prices(LPG_JSON)
    assert prices == [LpgPrice("dolnośląskie", date(2026, 9, 18), 2.68)]


async def test_get_motor_prices_success(mock_session, response_factory):
    mock_session.get.return_value = response_factory(200, MOTOR_JSON)
    client = OrlenApiClient(mock_session)
    prices = await client.async_get_motor_prices()
    assert set(prices) == {"Pb95", "ONEkodiesel"}
    assert prices["Pb95"].value_pln_per_m3 == 6344.0


async def test_get_lpg_prices_success(mock_session, response_factory):
    mock_session.get.return_value = response_factory(200, LPG_JSON)
    client = OrlenApiClient(mock_session)
    prices = await client.async_get_lpg_prices()
    assert prices["dolnośląskie"].netto_pln_per_l == 2.68


async def test_waf_html_body_raises(mock_session, response_factory):
    mock_session.get.return_value = response_factory(
        200, body=b"<html>Request Rejected</html>", content_type="text/html"
    )
    client = OrlenApiClient(mock_session)
    with pytest.raises(OrlenWafError):
        await client.async_get_motor_prices()


async def test_waf_content_type_raises(mock_session, response_factory):
    mock_session.get.return_value = response_factory(
        200, body=b"whatever", content_type="text/html; charset=utf-8"
    )
    client = OrlenApiClient(mock_session)
    with pytest.raises(OrlenWafError):
        await client.async_get_motor_prices()


async def test_401_raises_waf(mock_session, response_factory):
    mock_session.get.return_value = response_factory(401, {})
    client = OrlenApiClient(mock_session)
    with pytest.raises(OrlenWafError):
        await client.async_get_motor_prices()


async def test_500_raises_connection(mock_session, response_factory):
    mock_session.get.return_value = response_factory(500, {})
    client = OrlenApiClient(mock_session)
    with pytest.raises(OrlenConnectionError):
        await client.async_get_motor_prices()


async def test_invalid_json_raises_data_error(mock_session, response_factory):
    mock_session.get.return_value = response_factory(200, body=b"not json")
    client = OrlenApiClient(mock_session)
    with pytest.raises(OrlenDataError):
        await client.async_get_motor_prices()


async def test_client_error_raises_connection(mock_session):
    ctx = MagicMock()
    ctx.__aenter__ = AsyncMock(side_effect=aiohttp.ClientError("boom"))
    ctx.__aexit__ = AsyncMock(return_value=False)
    mock_session.get.return_value = ctx
    client = OrlenApiClient(mock_session)
    with pytest.raises(OrlenConnectionError):
        await client.async_get_motor_prices()


async def test_timeout_raises_connection(mock_session):
    ctx = MagicMock()
    ctx.__aenter__ = AsyncMock(side_effect=asyncio.TimeoutError())
    ctx.__aexit__ = AsyncMock(return_value=False)
    mock_session.get.return_value = ctx
    client = OrlenApiClient(mock_session)
    with pytest.raises(OrlenConnectionError):
        await client.async_get_motor_prices()
