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

## Planned milestones

1. API ingestion and daily demand series
2. Forecasting baselines and rolling-origin validation
3. Statistical forecasting
4. Lag-feature machine-learning benchmark
5. Category-level diagnostics
6. Prediction intervals and staffing translation
7. Forecast dashboard
8. Final portfolio quality pass
