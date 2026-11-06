# NYC 311 Service Demand Forecasting

A time-series forecasting portfolio project using NYC Open Data to forecast daily 311 service-request demand and evaluate how forecasts can support operational staffing and workload planning.

## Core question

How accurately can a city operations team forecast near-term 311 service-request volume, and how can forecast uncertainty inform staffing decisions?

## Project design

This project is intentionally forecasting-first.

It will demonstrate:

- public API ingestion
- daily time-series aggregation
- trend and seasonality analysis
- calendar effects
- naive and seasonal-naive baselines
- statistical forecasting
- lag-feature machine learning
- rolling-origin backtesting
- MAE, RMSE, and WAPE
- prediction intervals
- category-level forecast diagnostics
- workload and staffing translation
- reproducible validation

## Data source

Official source: NYC Open Data, **311 Service Requests from 2020 to Present**.

Dataset ID: `erm2-nwe9`

The source is updated daily. To preserve reproducibility, the initial benchmark uses a fixed analysis window from **2022-01-01 through 2026-09-30**.

## Milestone 1 — forecast benchmark, uncertainty, and staffing translation

**Complete**

The first benchmark uses 1,734 daily observations and six rolling-origin 28-day backtest folds.

| Model | Mean WAPE |
| --- | ---: |
| 28-day rolling mean | **7.29%** |
| Weekly ETS | **7.34%** |
| HistGradientBoosting | **7.73%** |
| Naive | **8.08%** |
| 7-day seasonal naive | **9.12%** |

The preferred model is the **28-day rolling mean**. More complex models were retained as benchmarks but were not selected because they did not improve the primary out-of-time accuracy metric.

Operational forecast:

- point forecast: **10,842 requests/day**
- empirical 80% error half-width: **1,314 requests/day**
- empirical 95% error half-width: **1,978 requests/day**

Illustrative staffing scenario:

- point forecast: **284 FTE**
- 80% upper demand band: **318 FTE**
- 95% upper demand band: **336 FTE**

The staffing conversion is an explicit scenario assumption, not an NYC staffing standard.

[Read the Milestone 1 findings](docs/MILESTONE1_FORECAST_BENCHMARK.md)

## Next milestone

Milestone 2 will add service-category forecasting and diagnostics to determine where demand is more or less predictable.
