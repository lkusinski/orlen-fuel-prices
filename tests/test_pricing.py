"""Unit tests for the pure pricing logic (VAT windows + margin)."""
from __future__ import annotations

from datetime import date

from custom_components.orlen_fuel_prices.pricing import (
    compute_price,
    gross,
    netto_from_value,
    vat_for,
    with_margin,
)


def test_netto_from_value_divides_by_1000():
    assert netto_from_value(6344.0) == 6.344
    assert netto_from_value(6088.0) == 6.088


def test_gross_default_23():
    assert gross(6.344, 23) == 7.803
    assert gross(6.088, 23) == 7.488


def test_vat_windows_cpn():
    assert vat_for("Pb95", date(2026, 4, 15)) == 8
    assert vat_for("Pb95", date(2026, 5, 15)) == 8
    assert vat_for("Pb95", date(2026, 6, 30)) == 8
    assert vat_for("Pb95", date(2026, 7, 1)) == 23
    assert vat_for("ONEkodiesel", date(2026, 8, 20)) == 8
    assert vat_for("ONEkodiesel", date(2026, 9, 1)) == 23


def test_vat_heating_stays_23():
    assert vat_for("OnEkoterm", date(2026, 4, 15)) == 23
    assert vat_for("HeatingC3", date(2026, 8, 20)) == 23


def test_vat_override_wins():
    assert vat_for("Pb95", date(2026, 9, 19), override=0) == 0
    assert vat_for("OnEkoterm", date(2026, 4, 15), override=5) == 5


def test_with_margin_default_zero():
    assert with_margin(7.803, 0) == 7.803


def test_with_margin_applies_percent():
    assert with_margin(7.803, 10) == 8.583


def test_compute_price_uses_effective_date_not_today():
    # Price from 2026-06-30 must use the 8% window even if read later.
    breakdown = compute_price(5228.0, "Pb95", date(2026, 6, 30))
    assert breakdown["vat"] == 8
    assert breakdown["netto"] == 5.228
    assert breakdown["brutto"] == 5.646


def test_compute_price_default_margin_equals_brutto():
    breakdown = compute_price(6344.0, "Pb95", date(2026, 9, 19))
    assert breakdown["brutto"] == 7.803
    assert breakdown["brutto_z_marza"] == breakdown["brutto"]


def test_compute_price_with_margin_included():
    breakdown = compute_price(
        6344.0, "Pb95", date(2026, 9, 19), margin=5.0
    )
    assert breakdown["brutto"] == 7.803
    assert breakdown["brutto_z_marza"] == 8.193


def test_compute_price_fixed_vat_mode_overrides_table():
    breakdown = compute_price(
        6344.0,
        "OnEkoterm",
        date(2026, 4, 15),
        vat_mode="fixed",
        vat_rate=0,
    )
    assert breakdown["vat"] == 0
    assert breakdown["brutto"] == 6.344
