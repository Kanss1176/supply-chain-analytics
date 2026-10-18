# Weekly status: Food and Beverage Demand-Supply Monitor

**Data through:** August 2026 (US Census M3, official API) | **Run date:** 18 October 2026
**Scope:** US food and beverage manufacturing, industry level. This is public data, not any company's own numbers.

## Summary
Food overall is steady: about 0.8 months of inventory on hand, shipments up 1.8% on a year ago. Two industries need a closer look: grain and cereal milling (shipments rising while stock cover thins) and dairy (stock cover above its usual range).

## What changed
| Industry | Aug 2026 months of supply | Shipments vs last year | Flag |
| --- | --- | --- | --- |
| Food products (total) | 0.81 | +1.8% | None |
| Grain and oilseed milling, breakfast cereal | 0.73 | +10.7% | Shipments above usual range for 6 months in a row (Mar-Aug); stock cover below usual range for 4 (May-Aug) |
| Dairy products | 0.91 | -3.8% | Stock cover above usual range in May and again in Aug |
| Meat, poultry and seafood processing | 0.50 | +1.3% | None |
| Beverage manufacturing | 2.51 | +1.9% | None now. Shipments growth sat below its usual range Oct 2025 to Jan 2026 |
| Beverage and tobacco (total) | 1.88 | +1.3% | None |

Sixteen flagged months in the last 12 months are five separate episodes (a run of consecutive flagged months counts as one).

## What to do
- **Grain and cereal:** check whether the rise in shipments is real demand or price. Stock cover at 0.73 months is at the low end of its range, so watch supply continuity.
- **Dairy:** inventory is building relative to shipments while shipments fall. Look at whether production should slow.
- **Beverage:** no action. Growth was soft over the winter and has returned to normal.

## How far to trust this
- Shipments are in current dollars, so price changes move them. A rise is not automatically more volume.
- The usual range is the previous 36 months, mean plus or minus 2 standard deviations. A flag means look, not that something is wrong.
- **Forecast check (last 12 months held out):** the model beat the "same month last year" baseline for meat (0.78% vs 0.97% error), beverage manufacturing (1.57% vs 2.01%) and beverage-and-tobacco total (1.25% vs 3.35%). It did **not** beat it for food total (1.01% vs 0.99%), grain and cereal (6.84% vs 4.71%) or dairy (4.08% vs 3.62%). For those three, use the baseline.
- M3 has no orders data for food and beverage industries, so backlog and order-to-ship ratios are not available.

## Next
- Power BI page: trend lines and the episode list.
- Monthly refresh when the Census publishes the next M3 release.
