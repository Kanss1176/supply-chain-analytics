# KPI definitions

All values come from the Census M3 monthly series for one industry at a time.

| KPI | Formula | How to read it |
| --- | --- | --- |
| Months of supply | End-of-month inventory / that month's shipments | How many months current inventory would last at the current shipping pace. Higher means more cover. |
| Backlog ratio | Unfilled orders / that month's shipments | Orders waiting relative to monthly output. |
| Order-to-ship ratio | New orders / shipments | Above 1: orders are arriving faster than shipments. Below 1: the backlog is shrinking or demand is softening. |
| Month-on-month change | (this month - last month) / last month | Short-term movement. Seasonal, so compare with the same month last year. |
| Year-on-year change | (this month - same month last year) / same month last year | Removes most seasonality. |
| Exception band | Previous 36 months' mean +/- 2 standard deviations | A month outside the band is flagged for review. It is a prompt to look, not proof of a problem. |

## Forecast evaluation

Holt-Winters is compared with a seasonal-naive baseline (same month last year) on the last 12 months, using mean absolute percentage error. A model that does not beat the baseline is reported as not beating it.
