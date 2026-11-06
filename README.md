# NYC 311 Service Demand Forecasting

[![Quality checks](https://github.com/fernandoverdugo/nyc-311-service-demand-forecasting/actions/workflows/quality-checks.yml/badge.svg)](https://github.com/fernandoverdugo/nyc-311-service-demand-forecasting/actions/workflows/quality-checks.yml)

A time-series forecasting portfolio project using NYC Open Data to forecast daily 311 service-request demand and evaluate how forecasts can support operational staffing and workload planning.

**Live dashboard:** https://fernandoverdugo.github.io/nyc-311-service-demand-forecasting/dashboard.html

## Core question

How accurately can a city operations team forecast near-term 311 service-request volume, and how can forecast uncertainty inform staffing decisions?

## Project design

This project is intentionally forecasting-first.

It demonstrates:

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

## Milestone 2 — service-category forecast diagnostics

**Complete**

The eight highest-volume complaint types were evaluated using the same six rolling-origin 28-day folds.

| Complaint type | Mean WAPE |
| --- | ---: |
| Illegal Parking | **8.6%** |
| Blocked Driveway | **9.1%** |
| Abandoned Vehicle | **20.5%** |
| UNSANITARY CONDITION | **27.3%** |
| Noise - Residential | **30.2%** |
| Street Condition | **34.1%** |
| Noise - Street/Sidewalk | **47.9%** |
| HEAT/HOT WATER | **53.0%** |

Median category WAPE is **28.8%**, compared with **7.3%** for the citywide aggregate.

The result shows that aggregation materially improves forecastability and that a single forecasting method should not be applied mechanically to every service line.

[Read the Milestone 2 findings](docs/MILESTONE2_CATEGORY_DIAGNOSTICS.md)

## Milestone 3 — category-specific seasonality and calendar models

**Complete**

Three volatile complaint types were retested with annual persistence and a recursive calendar/lag gradient-boosting model.

| Complaint type | Rolling mean WAPE | Best model | Best WAPE | Improvement |
| --- | ---: | --- | ---: | ---: |
| HEAT/HOT WATER | 53.0% | Annual naive (365d) | **35.2%** | **33.5%** |
| Noise - Street/Sidewalk | 47.9% | Calendar/lag HGB | **30.7%** | **35.9%** |
| Street Condition | 34.1% | Calendar/lag HGB | **23.7%** | **30.4%** |

The result reinforces the project's central forecasting lesson: model choice should follow the behavior of the series.

- citywide demand favors a simple recent-level forecast;
- HEAT/HOT WATER favors transparent annual persistence;
- street noise and street condition benefit from richer lag/calendar features.

[Read the Milestone 3 findings](docs/MILESTONE3_TARGETED_MODELS.md)

## Milestone 4 — stakeholder forecast dashboard

**Complete**

The validated forecasting outputs are now consolidated into a stakeholder-facing dashboard covering:

- citywide forecast demand and preferred-model accuracy;
- empirical 80% and 95% planning ranges;
- illustrative staffing translation;
- citywide model comparison;
- complaint-category forecastability;
- targeted model improvements for volatile service lines.

**[View the live stakeholder dashboard](https://fernandoverdugo.github.io/nyc-311-service-demand-forecasting/dashboard.html)**

[Read the Milestone 4 findings](docs/MILESTONE4_DASHBOARD.md)

## Current status

**Portfolio-ready**

The completed workflow is:

```text
NYC Open Data
      ↓
daily demand series
      ↓
rolling-origin model benchmark
      ↓
forecast uncertainty + staffing translation
      ↓
category forecast diagnostics
      ↓
category-specific model selection
      ↓
stakeholder dashboard
```

The central result is deliberately practical: model complexity is not treated as a goal. The project selects simple recent-level forecasting for citywide demand, annual persistence where strong seasonality supports it, and lag/calendar machine learning where it materially improves volatile categories.

## Reproduce the analysis

Requires Python 3.14.

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt

python src/fetch_daily_counts.py
python src/baseline_backtest.py
python src/statistical_backtest.py
python src/ml_backtest.py
python src/model_comparison.py
python src/summarize_benchmark.py
python src/operational_forecast.py

python src/fetch_targeted_category_counts.py
python src/targeted_category_backtest.py
python src/summarize_targeted_categories.py

python src/build_dashboard.py
python src/validate_dashboard.py
python src/validate_committed_benchmarks.py
python src/validate_project.py
```

Normal CI refreshes the live forecasting inputs used by Milestones 1 and 3 while retaining the validated eight-category Milestone 2 benchmark as committed metadata to avoid unnecessary load on NYC Open Data. A dedicated consistency check confirms that regenerated citywide, operational, and targeted-model results still match the committed benchmark metadata used by the README and dashboard.


## License

This project is licensed under the [MIT License](LICENSE).
