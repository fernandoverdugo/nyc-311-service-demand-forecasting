# Milestone 3 — Category-Specific Seasonality & Calendar Models

## Purpose

Milestone 3 tests whether volatile 311 complaint categories benefit from models matched to their demand structure rather than using the citywide preferred 28-day rolling mean everywhere.

Three categories were selected from Milestone 2 because they had comparatively high forecast error:

- HEAT/HOT WATER
- Noise - Street/Sidewalk
- Street Condition

Each model is evaluated using the same design:

- fixed analysis window: 2022-01-01 through 2026-09-30
- daily aggregation
- 28-day forecast horizon
- six rolling-origin backtest folds
- WAPE as the primary selection metric

## Models compared

### 28-day rolling mean

The Milestone 1 citywide preferred model and the category-level baseline.

### 365-day annual naive

Uses demand from the same dates one year earlier.

This provides a transparent test of annual persistence and is especially relevant for categories with strong seasonal behavior.

### Calendar/lag HistGradientBoosting

A recursive gradient-boosting forecast using only information available before each forecast date.

Features include:

- 1-day lag
- 7-day lag
- 14-day lag
- 28-day lag
- 365-day lag
- 7-day rolling mean
- 28-day rolling mean
- 90-day rolling mean
- day of week
- weekend indicator
- annual sine/cosine calendar terms

## Results

| Complaint type | Rolling mean WAPE | Best model | Best WAPE | Improvement |
| --- | ---: | --- | ---: | ---: |
| HEAT/HOT WATER | 53.0% | Annual naive (365d) | **35.2%** | **33.5%** |
| Noise - Street/Sidewalk | 47.9% | Calendar/lag HGB | **30.7%** | **35.9%** |
| Street Condition | 34.1% | Calendar/lag HGB | **23.7%** | **30.4%** |

All three targeted categories improved materially over the citywide-style rolling-mean benchmark.

## HEAT/HOT WATER

The annual-naive model reduced WAPE from **53.0% to 35.2%**, an improvement of **33.5%**.

The calendar/lag gradient-boosting model also improved substantially, reaching **36.9% WAPE**, but annual persistence remained slightly better on the primary selection metric.

This result is useful because it shows that a transparent seasonal benchmark can outperform a more complex model when demand has strong recurring annual structure.

## Noise - Street/Sidewalk

The calendar/lag gradient-boosting model reduced WAPE from **47.9% to 30.7%**, an improvement of **35.9%**.

The 365-day annual-naive model performed worse than the rolling mean at **51.1% WAPE**, suggesting that annual persistence alone does not adequately capture this category's short-term variation.

Calendar effects, recent lags, and rolling demand levels provide materially more useful information.

## Street Condition

The calendar/lag model reduced WAPE from **34.1% to 23.7%**, an improvement of **30.4%**.

Annual naive performed poorly at **42.0% WAPE**, again showing that repeating the previous year's level is not automatically appropriate simply because a series has seasonal variation.

## Portfolio takeaway

The project now demonstrates three distinct forecasting lessons:

1. **Citywide demand:** a simple recent-level forecast can outperform more complex models.
2. **Strong annual seasonality:** a transparent annual-naive forecast can outperform machine learning.
3. **Mixed calendar and recent-history effects:** lag/calendar machine learning can materially improve volatile service categories.

The modeling strategy therefore follows the behavior of each time series rather than selecting one algorithm for every problem.

## Pipeline design improvement

Normal CI now avoids re-running the full eight-category discovery pipeline on every commit.

Instead:

- the validated Milestone 2 category benchmark is retained as committed metadata;
- Milestone 3 live-refreshes only the three categories it actively models;
- all targeted series still receive complete date-grid, fold-count, model-set, and metric validation.

This reduces unnecessary load on NYC Open Data while preserving reproducibility and auditability.

## Status

**Complete**

The next milestone should turn the forecasting outputs into a stakeholder-facing forecast dashboard showing model accuracy, uncertainty, category forecastability, and staffing scenarios.
