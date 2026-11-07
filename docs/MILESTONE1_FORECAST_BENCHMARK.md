# Milestone 1 — Forecast Benchmark, Uncertainty & Staffing Translation

## Scope

Milestone 1 establishes a reproducible forecasting benchmark for daily NYC 311 request volume.

The benchmark uses:

- **1,734 daily observations**
- **16,496,781 total requests**
- fixed analysis window: **2022-01-01 through 2026-09-30**
- **28-day forecast horizon**
- **6 rolling-origin backtest folds**
- primary metric: **WAPE**

## Model comparison

| Model | Mean WAPE |
| --- | ---: |
| 28-day rolling mean | **7.29%** |
| Weekly ETS | **7.34%** |
| HistGradientBoosting | **7.73%** |
| Naive | **8.08%** |
| 7-day seasonal naive | **9.12%** |

The preferred model is the **28-day rolling mean** because it produced the lowest mean out-of-time WAPE.

This is a deliberate model-selection result: more complex models were evaluated under the same rolling-origin design and were not preferred when they failed to improve the primary accuracy metric.

## Preferred-model accuracy

- MAE: **790 requests/day**
- RMSE: **966 requests/day**
- WAPE: **7.29%**

The rolling-mean benchmark improved WAPE by about **20.1%** relative to the 7-day seasonal-naive benchmark.

## Operational forecast

Using the full fixed analysis window, the preferred model produces a 28-day point forecast of approximately:

**10,842 requests per day**

Empirical absolute errors from rolling-origin backtests are used to construct operational uncertainty bands.

- 80% empirical half-width: **1,314 requests/day**
- 95% empirical half-width: **1,978 requests/day**

These are empirical planning bands based on historical backtest errors, not parametric confidence intervals.

## Staffing translation

To connect the demand forecast with operational planning, the project uses an explicit illustrative scenario:

- 45 requests handled per FTE per day
- 85% target utilization

Under those assumptions:

| Planning level | Daily staffing |
| --- | ---: |
| Point forecast | **284 FTE** |
| 80% upper demand band | **318 FTE** |
| 95% upper demand band | **336 FTE** |

These values are **not NYC staffing standards** and should not be interpreted as claims about actual agency productivity or staffing needs. They are transparent scenario assumptions used for forecast-to-capacity translation.

## Infrastructure reliability

The ingestion pipeline retries transient NYC Open Data failures, including:

- HTTP 429
- HTTP 5xx errors
- connection failures
- read timeouts

GitHub Actions also cancels superseded workflow runs so multiple commits do not create unnecessary concurrent requests to the public API.

## Status

**Complete**

The subsequent category analysis adds service-category forecasting and diagnostics to assess whether forecast accuracy varies meaningfully across request types.
