# Risks log: food and beverage monitor

Risks to the weekly monitor and the decisions that rely on it. Likelihood and impact are rated High, Medium or Low. Owner is the role that watches the risk.

| # | Risk | Likelihood | Impact | Owner | Mitigation | Status |
|---|------|------------|--------|-------|------------|--------|
| 1 | The forecast does not beat a "same month last year" baseline for the food total, grain and cereal, or dairy, so planners may trust a weak forecast | High | Medium | Analyst | Label the forecast as not reliable on the dashboard and in the README. Show the baseline next to it. Re-run the backtest each quarter. | Open |
| 2 | M3 covers US manufacturers only, not India, Asia-Pacific, Middle East or South Africa, so the monitor may not reflect other markets | High | High | Analyst and planner | State the limit in the README and the status one-pager. Look for regional data before using the monitor outside the US. | Open |
| 3 | Shipments are in current dollars, so price changes look like demand changes | High | Medium | Analyst | Add a note on the dashboard. Read shipments growth together with months of supply. | Open |
| 4 | No orders data for food and beverage, so there are no backlog or order-to-ship measures | High | Medium | Analyst | Say so in the README. Use months of supply as the main measure. | Accepted |
| 5 | Census publishes a new month late, or the API is down, so the monitor shows old data | Medium | Medium | Analyst | Show the data month on the dashboard. Add a check that stops the build if the newest month has not changed. | Open |
| 6 | A category code is added or renamed, so an industry is missing or mapped wrongly | Low | High | Analyst | Run `explore_m3.py` each week and compare codes with the mapping. | Open |
| 7 | The Power BI file is refreshed by hand and may be out of date | Medium | Medium | Analyst | Show the build date on both pages. Follow the refresh step in the process map. | Open |
| 8 | A small move looks large because the chart axis is narrow (the food total stays below one month of supply) | Medium | Low | Analyst | Explain this in the README under "How to read it". | Mitigated |
| 9 | Tests pass but live data has a new problem that the tests do not cover | Low | Medium | Analyst | Check the flagged episodes and latest month by eye before writing the status. | Open |

## How risks are escalated

1. A new risk is added to this table with a rating and an owner.
2. A High impact risk is raised in the weekly status one-pager.
3. The planner decides whether to accept it, act on it or ask for more data.
4. Status is updated to Open, Mitigated or Accepted at each weekly review.