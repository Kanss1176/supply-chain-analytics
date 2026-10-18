"""Tests for the KPI and forecast logic.

The numbers below are tiny TOY values chosen so the answers can be checked by hand.
They test the code's logic only. They are not data and are never shown as results.
"""
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "pepsico_planning"))

import forecast  # noqa: E402
import kpis  # noqa: E402


def monthly(values, start="2015-01-01"):
    return pd.Series(values, index=pd.date_range(start, periods=len(values), freq="MS"), dtype=float)


def test_months_of_supply_by_hand():
    inv = monthly([300, 200])
    ship = monthly([100, 100])
    assert kpis.months_of_supply(inv, ship).tolist() == [3.0, 2.0]


def test_zero_shipments_gives_nan_not_error():
    result = kpis.months_of_supply(monthly([10]), monthly([0]))
    assert np.isnan(result.iloc[0])


def test_order_to_ship_above_one_means_demand_outruns_shipments():
    assert kpis.order_to_ship(monthly([120]), monthly([100])).iloc[0] == pytest.approx(1.2)


def test_yoy_compares_same_month_last_year():
    s = monthly([100] * 12 + [110])
    assert kpis.yoy(s).iloc[-1] == pytest.approx(0.10)


def test_band_flags_a_spike_and_not_normal_months():
    base = [100, 101, 99, 100, 102, 98] * 6  # 36 calm months
    s = monthly(base + [160])
    flags = kpis.trailing_band_flags(s, window=36, k=2.0, min_periods=24)
    assert flags["flag"].iloc[-1] == "high"
    assert (flags["flag"].iloc[:-1] == "").all()


def test_band_does_not_flag_before_enough_history():
    s = monthly([100, 500, 100, 500])
    assert (kpis.trailing_band_flags(s)["flag"] == "").all()


def test_mape_by_hand():
    assert forecast.mape(pd.Series([100, 200]), pd.Series([110, 180])) == pytest.approx(10.0)


def test_seasonal_naive_repeats_last_year():
    train = monthly(list(range(1, 25)))  # 24 months
    out = forecast.seasonal_naive(train, 3)
    assert out.tolist() == [13.0, 14.0, 15.0]
    assert out.index[0] == pd.Timestamp("2017-01-01")


def test_backtest_runs_and_reports_both_methods():
    rng = np.random.default_rng(0)
    t = np.arange(72)
    toy = 100 + 0.2 * t + 10 * np.sin(2 * np.pi * t / 12) + rng.normal(0, 1, 72)
    result = forecast.backtest(monthly(toy), holdout=12)
    assert result["mape_holt_winters"] >= 0
    assert result["mape_seasonal_naive"] >= 0
    assert isinstance(result["model_beats_baseline"], bool)


def test_backtest_refuses_short_history():
    with pytest.raises(ValueError):
        forecast.backtest(monthly(list(range(30))), holdout=12)


def test_backtest_refuses_gaps():
    s = monthly(list(range(1, 73)))
    s.iloc[10] = np.nan
    # a NaN is dropped, leaving a gap in the monthly index
    with pytest.raises(ValueError):
        forecast.backtest(s, holdout=12)
