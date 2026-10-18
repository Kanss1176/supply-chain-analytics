"""Group flagged months into episodes.

A trailing-band flag fires every month while a series drifts outside its usual range, so six
flagged months in a row are one story, not six. An episode is a run of consecutive flagged
months for the same industry, metric and direction.
"""
import pandas as pd


def group_episodes(exceptions: pd.DataFrame, latest_month) -> pd.DataFrame:
    cols = ["category_code", "industry", "metric", "direction", "start", "end", "months",
            "still_active", "peak_value"]
    if exceptions.empty:
        return pd.DataFrame(columns=cols)
    rows = []
    keys = ["category_code", "industry", "metric", "direction"]
    for key, g in exceptions.groupby(keys):
        g = g.sort_values("month")
        months = pd.DatetimeIndex(pd.to_datetime(g["month"]))
        values = g["value"].to_numpy()
        run_start = 0
        for i in range(1, len(months) + 1):
            broke = i == len(months) or (months[i].year * 12 + months[i].month) - (
                months[i - 1].year * 12 + months[i - 1].month) != 1
            if broke:
                run = values[run_start:i]
                peak = run.max() if key[3] == "high" else run.min()
                rows.append(dict(zip(keys, key), start=months[run_start], end=months[i - 1],
                                 months=i - run_start,
                                 still_active=bool(months[i - 1] == pd.Timestamp(latest_month)),
                                 peak_value=float(peak)))
                run_start = i
    return pd.DataFrame(rows, columns=cols).sort_values("end", ascending=False).reset_index(drop=True)
