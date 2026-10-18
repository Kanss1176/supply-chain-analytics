"""Toy-value tests for episode grouping (logic only, not data)."""
import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "pepsico_planning"))
from episodes import group_episodes  # noqa: E402


def _exc(months, value=1.0, direction="high"):
    return pd.DataFrame({"month": pd.to_datetime(months), "category_code": "X", "industry": "Toy",
                         "metric": "m", "value": value, "direction": direction})


def test_consecutive_months_make_one_episode():
    out = group_episodes(_exc(["2026-03-01", "2026-04-01", "2026-05-01"]), "2026-05-01")
    assert len(out) == 1 and out.loc[0, "months"] == 3 and out.loc[0, "still_active"]


def test_gap_splits_episodes():
    out = group_episodes(_exc(["2025-01-01", "2025-02-01", "2025-05-01"]), "2026-01-01")
    assert sorted(out["months"]) == [1, 2] and not out["still_active"].any()


def test_peak_is_max_for_high_and_min_for_low():
    hi = group_episodes(_exc(["2026-01-01", "2026-02-01"], value=[1.0, 3.0]), "2026-02-01")
    lo = group_episodes(_exc(["2026-01-01", "2026-02-01"], value=[1.0, 3.0], direction="low"), "2026-02-01")
    assert hi.loc[0, "peak_value"] == 3.0 and lo.loc[0, "peak_value"] == 1.0
