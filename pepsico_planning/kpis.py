"""Planning KPIs for one monthly series. Pure functions: no downloads, easy to test.

Definitions (also in docs/kpi_definitions.md):
  months_of_supply   = end-of-month inventory / that month's shipments
  backlog_ratio      = unfilled orders / that month's shipments
  order_to_ship      = new orders / shipments (above 1 means demand is outrunning shipments)
  yoy                = change versus the same month a year earlier
"""
import numpy as np
import pandas as pd


def safe_ratio(numerator: pd.Series, denominator: pd.Series) -> pd.Series:
    """numerator / denominator, with NaN where the denominator is zero or missing."""
    den = denominator.where(denominator != 0)
    return numerator / den


def months_of_supply(inventory: pd.Series, shipments: pd.Series) -> pd.Series:
    return safe_ratio(inventory, shipments)


def backlog_ratio(unfilled_orders: pd.Series, shipments: pd.Series) -> pd.Series:
    return safe_ratio(unfilled_orders, shipments)


def order_to_ship(new_orders: pd.Series, shipments: pd.Series) -> pd.Series:
    return safe_ratio(new_orders, shipments)


def mom(series: pd.Series) -> pd.Series:
    """Month-on-month percentage change."""
    return series.pct_change(periods=1)


def yoy(series: pd.Series) -> pd.Series:
    """Year-on-year percentage change for a monthly series."""
    return series.pct_change(periods=12)


def trailing_band_flags(series: pd.Series, window: int = 36, k: float = 2.0, min_periods: int = 24) -> pd.DataFrame:
    """Flag months outside mean +/- k standard deviations of the PREVIOUS `window` months.

    The band uses only earlier months (shift by one), so a month is never compared with itself.
    Returns columns: value, band_low, band_high, flag ('high', 'low' or '').
    """
    past = series.shift(1)
    mean = past.rolling(window, min_periods=min_periods).mean()
    std = past.rolling(window, min_periods=min_periods).std()
    low = mean - k * std
    high = mean + k * std
    flag = np.where(series > high, "high", np.where(series < low, "low", ""))
    flag = pd.Series(flag, index=series.index).where(high.notna(), "")
    return pd.DataFrame({"value": series, "band_low": low, "band_high": high, "flag": flag})
