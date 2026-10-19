# Process map: weekly food and beverage monitor

This is the weekly routine that turns the US Census M3 data into a one-page status for planners. Each step names who does it, what it produces and where it can go wrong.

## Flow

```mermaid
flowchart LR
    A[Download M3 data] --> B[Check codes and data]
    B --> C[Build monitor]
    C --> D[Refresh Power BI]
    D --> E[Write status one-pager]
    E --> F[Planner review]
```

## Steps

| # | Step | Who | Tool or file | Output | Where it can go wrong |
|---|------|-----|--------------|--------|-----------------------|
| 1 | Download the latest M3 data from the Census API | Analyst | `fetch_m3.py` | Raw monthly data in `data/` | API is slow or down. Census has not yet published the new month. |
| 2 | Check categories and industry mapping | Analyst | `explore_m3.py` | Category codes mapped to industries | A code is added or renamed and the industry mapping is out of date. |
| 3 | Build the monitor: load data, calculate KPIs, flag exceptions and episodes, run the forecast | Analyst | `build_monitor.py`, `kpis.py`, `episodes.py`, `forecast.py` | `outputs/monitor.xlsx` | Script error. A KPI is calculated differently from `kpi_definitions.md`. |
| 4 | Run the tests | Analyst | `python -m pytest` | Pass or fail | Tests pass but the live data has a new problem the tests do not cover. |
| 5 | Refresh the Power BI dashboard | Analyst | `food_beverage_monitor.pbix` | Page 1 (overview) and Page 2 (flagged episodes) | Date columns split into Year, Quarter, Month and Day. Numbers get summed instead of shown as they are. |
| 6 | Write the weekly status one-pager | Analyst | `docs/weekly_status.md` | Status for the latest month | A number is copied wrongly from the dashboard. A flagged episode is not explained. |
| 7 | Planner review and follow-up | Planner | Dashboard and one-pager | Decision on which months and industries to watch | The planner reads a small move as large because the chart axis is narrow. |

## Pain points found while building this

- **Narrow chart axis.** Months of supply for the food total stays below one month, so a small move looks large.
- **Shipments are in current dollars.** Price changes move the numbers, so growth is not the same as volume.
- **No orders data for food and beverage.** There are no backlog or order-to-ship measures.
- **Forecast does not beat a "same month last year" baseline** for the food total, grain and cereal, or dairy. It is shown for transparency, not as a reliable prediction.
- **Manual refresh in Power BI.** The dashboard is refreshed by hand after the Excel file is rebuilt, so it can be out of date.

## Improvement ideas

1. Add a check in `build_monitor.py` that stops with a clear message if the newest month is the same as last week's.
2. Show the data month and the date the monitor was built on both dashboard pages.
3. Add a short note on the dashboard that shipments are in current dollars.
4. Record each week's flagged episodes so changes from week to week can be seen.