"""Seasonal forecast with an honest backtest.

Two methods are compared on held-out months:
  1. seasonal naive: next month = same month last year (the baseline any model must beat)
  2. Holt-Winters exponential smoothing (statsmodels)
The error measure is MAPE (mean absolute percentage error). If the model does not beat the
baseline, the report says so; do not hide that.
"""
import numpy as np
import pandas as pd
from statsmodels.tsa.holtwinters import ExponentialSmoothing


def _as_monthly(series: pd.Series) -> pd.Series:
    s = series.dropna().copy()
    s.index = pd.DatetimeIndex(s.index).to_period("M").to_timestamp()
    return s.asfreq("MS")


def mape(actual: pd.Series, predicted: pd.Series) -> float:
    actual = np.asarray(actual, dtype=float)
    predicted = np.asarray(predicted, dtype=float)
    return float(np.mean(np.abs((actual - predicted) / actual)) * 100)


def seasonal_naive(train: pd.Series, horizon: int) -> pd.Series:
    """Repeat the last 12 observed months forward."""
    last_year = train.iloc[-12:].to_numpy()
    values = np.resize(last_year, horizon)
    idx = pd.date_range(train.index[-1] + pd.offsets.MonthBegin(1), periods=horizon, freq="MS")
    return pd.Series(values, index=idx)


def holt_winters(train: pd.Series, horizon: int) -> pd.Series:
    model = ExponentialSmoothing(
        train, trend="add", damped_trend=True, seasonal="add", seasonal_periods=12
    ).fit()
    return model.forecast(horizon)


def backtest(series: pd.Series, holdout: int = 12) -> dict:
    """Fit on all but the last `holdout` months, score both methods on those months."""
    s = _as_monthly(series)
    if s.isna().any():
        raise ValueError("Series has gaps; fix or fill them before forecasting.")
    if len(s) < holdout + 36:
        raise ValueError("Need at least holdout + 36 months of history.")
    train, test = s.iloc[:-holdout], s.iloc[-holdout:]
    naive = seasonal_naive(train, holdout)
    hw = holt_winters(train, holdout)
    result = {
        "holdout_months": holdout,
        "mape_seasonal_naive": mape(test, naive),
        "mape_holt_winters": mape(test, hw),
    }
    result["model_beats_baseline"] = result["mape_holt_winters"] < result["mape_seasonal_naive"]
    return result


def forecast_ahead(series: pd.Series, horizon: int = 6) -> pd.Series:
    """Forecast beyond the last observed month with Holt-Winters."""
    s = _as_monthly(series)
    return holt_winters(s, horizon)
