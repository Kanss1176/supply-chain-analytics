# supply-chain-analytics

Analytics modules built on **real public data**. Nothing here is invented or simulated.

## Module 1: Food and Beverage Demand-Supply Monitor (`pepsico_planning/`)

**Question:** Is demand for US food and beverage manufacturing running ahead of or behind supply, and which months deserve a planner's attention?

**Data:** US Census Bureau, *Manufacturers' Shipments, Inventories and Orders (M3)*, downloaded from the official API
(`https://api.census.gov/data/timeseries/eits/m3`). Monthly, public.

**Limitation:** M3 covers US manufacturers. It is not data from any single company, and it does not cover Asia-Pacific, India, Middle East or South Africa markets.

### Status

| Step | State |
| --- | --- |
| Download script (`fetch_m3.py`) | Written, not yet run on live data |
| Code discovery (`explore_m3.py`) | Written, not yet run on live data |
| KPI functions (`kpis.py`) | Written, unit-tested on toy values |
| Forecast and backtest (`forecast.py`) | Written, unit-tested on toy values |
| Map category codes to industries | Next: needs real output of `explore_m3.py` |
| DuckDB load, exceptions table | Next |
| Excel workbook, Power BI dashboard | Next |
| Process map, risks log, status one-pager | Next |

### Run

```
python -m pip install -r requirements.txt
python pepsico_planning/fetch_m3.py
python pepsico_planning/explore_m3.py
python -m pytest
```

See `docs/kpi_definitions.md` for how each KPI is calculated.
