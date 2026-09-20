"""Tests for const helpers and catalog invariants."""
from __future__ import annotations

from custom_components.orlen_fuel_prices.const import (
    DEFAULT_MARGIN,
    DEFAULT_PRODUCTS,
    DEFAULT_VAT,
    HEATING_PRODUCTS,
    LPG_REGIONS,
    PRODUCT_LABELS,
    as_bool,
    as_float,
)


def test_as_float():
    assert as_float("3.5", 0) == 3.5
    assert as_float(None, 23) == 23
    assert as_float("abc", 1) == 1


def test_as_bool():
    assert as_bool(True) is True
    assert as_bool("false", True) is False
    assert as_bool(None, True) is True


def test_defaults_are_safe():
    assert DEFAULT_VAT == 23
    assert DEFAULT_MARGIN == 0.0


def test_catalog_consistency():
    assert set(DEFAULT_PRODUCTS).issubset(set(PRODUCT_LABELS))
    assert "OnEkoterm" in HEATING_PRODUCTS
    assert len(LPG_REGIONS) == 16


def test_default_products_are_not_heating_only():
    # Package parity: the default set mirrors the previous YAML package.
    assert "Pb95" in DEFAULT_PRODUCTS
    assert "ONEkodiesel" in DEFAULT_PRODUCTS
