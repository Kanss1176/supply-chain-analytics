"""Build the Food and Beverage Demand-Supply Monitor from the real Census M3 download.

Run:   python pepsico_planning/build_monitor.py
Needs: data/raw/m3_raw.csv (from fetch_m3.py)
Makes: data/monitor.duckdb, outputs/exceptions.csv, outputs/episodes.csv, outputs/forecast_backtest.csv,
       outputs/forecast_next6.csv, outputs/monitor.xlsx, outputs/build_log.txt

Series used (codes checked against Census M3 Appendix B and against the file itself):
  11S food products (total)      11A grain/oilseed milling + breakfast cereal
  11B dairy                      11C meat/seafood processing
  12A beverage manufacturing     12S beverage + tobacco (total)
Nondurable industries have shipments and inventories only: M3 publishes no new or unfilled
orders for them, so backlog and order-to-ship ratios are NOT computed.
"""
from pathlib import Path

import duckdb
import pandas as pd

from episodes import group_episodes
from forecast import backtest, forecast_ahead
from kpis import months_of_supply, mom, trailing_band_flags, yoy

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw" / "m3_raw.csv"
OUT = ROOT / "outputs"
DB = ROOT / "data" / "monitor.duckdb"

SERIES = {
    "11S": "Food products (total)",
    "11A": "Grain and oilseed milling, breakfast cereal",
    "11B": "Dairy products",
    "11C": "Meat, poultry and seafood processing",
    "12A": "Beverage manufacturing",
    "12S": "Beverage and tobacco products (total)",
}
STAGE_CATEGORIES = ["11S", "12S"]  # materials / work-in-process / finished-goods inventory exist only here
LOG = []


def log(msg: str) -> None:
    print(msg)
    LOG.append(msg)


def wide(raw: pd.DataFrame, cat: str, adj: str) -> pd.DataFrame:
    d = raw[(raw.category_code == cat) & (raw.seasonally_adj == adj)]
    w = d.pivot_table(index="month", columns="data_type_code", values="value", aggfunc="first").sort_index()
    w.index = pd.DatetimeIndex(w.index)
    return w


def main() -> None:
    OUT.mkdir(exist_ok=True)
    raw = pd.read_csv(RAW, parse_dates=["month"])
    raw = raw[raw.category_code.isin(SERIES)]
    log(f"Rows used: {len(raw)}; months {raw.month.min():%Y-%m} to {raw.month.max():%Y-%m}")

    kpi_rows, exc_rows, bt_rows, fc_rows = [], [], [], []
    for cat, name in SERIES.items():
        sa, nsa = wide(raw, cat, "yes"), wide(raw, cat, "no")
        if sa.empty or "VS" not in sa or "TI" not in sa:
            log(f"{cat}: skipped (shipments/inventory not published)")
            continue

        k = pd.DataFrame(index=sa.index)
        k["shipments_sa"], k["inventory_sa"] = sa["VS"], sa["TI"]
        k["shipments_nsa"], k["inventory_nsa"] = nsa["VS"], nsa["TI"]
        k["months_of_supply"] = months_of_supply(sa["TI"], sa["VS"])
        k["shipments_yoy"] = yoy(nsa["VS"])
        k["inventory_yoy"] = yoy(nsa["TI"])
        k["shipments_mom_sa"] = mom(sa["VS"])
        if cat in STAGE_CATEGORIES:
            for col, short in [("MI", "materials_inv_sa"), ("WI", "wip_inv_sa"), ("FI", "finished_inv_sa")]:
                if col in sa:
                    k[short] = sa[col]
        # cross-check against Census's own published inventory/shipments ratio
        if "IS" in sa:
            diff = (k["months_of_supply"] - sa["IS"]).abs().max()
            log(f"{cat}: my months-of-supply vs Census IS ratio, largest gap = {diff:.3f}")
        k.insert(0, "category_code", cat)
        k.insert(1, "industry", name)
        kpi_rows.append(k.reset_index().rename(columns={"index": "month"}))

        # exceptions: seasonally adjusted so normal seasonality does not trigger flags
        for metric, series in [("months_of_supply", k["months_of_supply"]),
                               ("shipments_yoy", k["shipments_yoy"])]:
            f = trailing_band_flags(series.dropna())
            for month, r in f[f.flag != ""].iterrows():
                direction = "above" if r.flag == "high" else "below"
                label = "months of supply" if metric == "months_of_supply" else "shipments year-on-year change"
                note = (f"{name}: {label} was {r.value:.3g}, {direction} its usual range of "
                        f"{r.band_low:.3g} to {r.band_high:.3g} (previous 36 months, mean +/- 2 SD). Review, not proof of a problem.")
                exc_rows.append({"month": month, "category_code": cat, "industry": name, "metric": metric,
                                 "value": r.value, "band_low": r.band_low, "band_high": r.band_high,
                                 "direction": r.flag, "note": note})

        # forecast shipments (not seasonally adjusted: the model should learn the seasonality)
        ship = nsa["VS"].dropna()
        try:
            bt = backtest(ship)
            bt.update(category_code=cat, industry=name, series="shipments_nsa")
            bt_rows.append(bt)
            verdict = "beats" if bt["model_beats_baseline"] else "does NOT beat"
            log(f"{cat}: Holt-Winters MAPE {bt['mape_holt_winters']:.2f}% vs seasonal-naive {bt['mape_seasonal_naive']:.2f}% -> {verdict} baseline")
            fc = forecast_ahead(ship, 6)
            for m, v in fc.items():
                fc_rows.append({"month": m, "category_code": cat, "industry": name,
                                "forecast_shipments_nsa": v, "model_beats_baseline": bt["model_beats_baseline"]})
        except ValueError as e:
            log(f"{cat}: forecast skipped: {e}")

    kpis = pd.concat(kpi_rows, ignore_index=True)
    exc = pd.DataFrame(exc_rows).sort_values("month", ascending=False)
    bt = pd.DataFrame(bt_rows)
    fc = pd.DataFrame(fc_rows)

    eps = group_episodes(exc, kpis.month.max())
    exc.to_csv(OUT / "exceptions.csv", index=False)
    eps.to_csv(OUT / "episodes.csv", index=False)
    bt.to_csv(OUT / "forecast_backtest.csv", index=False)
    fc.to_csv(OUT / "forecast_next6.csv", index=False)

    if DB.exists():
        DB.unlink()
    con = duckdb.connect(str(DB))
    for name, df in [("kpis", kpis), ("exceptions", exc), ("episodes", eps), ("forecast_backtest", bt), ("forecast_next6", fc)]:
        con.register("df_tmp", df)
        con.execute(f"CREATE TABLE {name} AS SELECT * FROM df_tmp")
        con.unregister("df_tmp")
    latest = con.execute("""
        SELECT category_code, industry, strftime(month, '%Y-%m') AS month,
               round(months_of_supply, 2) AS months_of_supply, round(shipments_yoy * 100, 1) AS shipments_yoy_pct
        FROM kpis WHERE month = (SELECT max(month) FROM kpis) ORDER BY category_code""").df()
    con.close()
    log("\nLatest month:\n" + latest.to_string(index=False))
    recent = eps[eps.end >= kpis.month.max() - pd.DateOffset(months=11)]
    log(f"\nFlagged months over whole history: {len(exc)} (= {len(eps)} episodes); in last 12 months: "
        f"{(exc.month >= kpis.month.max() - pd.DateOffset(months=11)).sum()} flagged months = {len(recent)} episodes")

    with pd.ExcelWriter(OUT / "monitor.xlsx", engine="openpyxl") as xw:
        pd.DataFrame({"About": [
            "Source: US Census Bureau, Manufacturers' Shipments, Inventories and Orders (M3), official API.",
            "Scope: US manufacturers by industry. Not data from any single company.",
            "Months of supply = inventory / shipments (seasonally adjusted). Same as Census's own inventories-to-shipments ratio.",
            "No backlog or order-to-ship measures: M3 publishes no orders data for food or beverage industries.",
            "Exceptions: month outside previous-36-month mean +/- 2 SD. A prompt to look, not proof of a problem.",
            "Episodes: consecutive flagged months for the same series, grouped so one drift is read as one story.",
            "Shipments are in current dollars, so price changes (for example 2021-2022) also move them; they are not volumes.",
            "Forecast: Holt-Winters on not-seasonally-adjusted shipments, backtested on last 12 months vs seasonal-naive.",
        ]}).to_excel(xw, sheet_name="About", index=False)
        kpis.to_excel(xw, sheet_name="KPIs", index=False)
        eps.to_excel(xw, sheet_name="Episodes", index=False)
        exc.to_excel(xw, sheet_name="Exceptions", index=False)
        bt.to_excel(xw, sheet_name="Forecast backtest", index=False)
        fc.to_excel(xw, sheet_name="Forecast next 6", index=False)
    (OUT / "build_log.txt").write_text("\n".join(LOG), encoding="utf-8")
    log(f"\nSaved to {OUT}")


if __name__ == "__main__":
    main()
