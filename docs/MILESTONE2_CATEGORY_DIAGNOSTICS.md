# Milestone 2 — Service-Category Forecast Diagnostics

## Purpose

Milestone 2 tests whether the citywide forecasting result generalizes to major 311 complaint categories.

The eight highest-volume complaint types in the fixed analysis window are evaluated separately using the same operational design:

- 2022-01-01 through 2026-09-30
- daily aggregation
- 28-day forecast horizon
- six rolling-origin backtest folds
- WAPE as the primary accuracy metric

The initial category diagnostic uses the preferred citywide benchmark: the 28-day rolling mean.

## Categories

| Complaint type | Requests |
| --- | ---: |
| Illegal Parking | **2,434,412** |
| Noise - Residential | **1,800,082** |
| HEAT/HOT WATER | **1,289,976** |
| Blocked Driveway | **812,009** |
| Noise - Street/Sidewalk | **780,567** |
| UNSANITARY CONDITION | **559,238** |
| Street Condition | **391,653** |
| Abandoned Vehicle | **322,172** |

## Forecastability

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

Median category WAPE is **28.8%**, substantially higher than the **7.3%** citywide benchmark.

## Interpretation

Aggregation materially improves forecastability.

Citywide daily demand smooths variation across service types, while individual categories retain distinct seasonal, weather-sensitive, event-sensitive, and behavioral patterns.

Two categories stand out as relatively stable under a recent-level forecast:

- **Illegal Parking — 8.6% WAPE**
- **Blocked Driveway — 9.1% WAPE**

Other categories are much less suitable for a single constant 28-day level forecast.

### HEAT/HOT WATER

HEAT/HOT WATER has the highest observed WAPE at **53.0%** despite being one of the largest categories by volume.

This is consistent with a demand series whose level can change sharply across weather and heating conditions. The result does not imply that the category is inherently unpredictable; it shows that a recent-level model is inadequate for this type of demand.

### Noise - Street/Sidewalk

Street/Sidewalk Noise records **47.9% WAPE**, indicating substantial short-term variation relative to its average volume.

A calendar- or event-sensitive forecast may be more appropriate than the citywide rolling-mean benchmark.

## Operational implication

A single forecasting method should not be applied mechanically across service lines.

A reasonable operations strategy is:

1. use simple recent-level forecasts for stable, high-volume categories;
2. use seasonality-aware or external-driver models for weather-sensitive categories;
3. retain wider planning bands for volatile service types;
4. evaluate staffing at both aggregate and category levels.

## Data engineering

The category pipeline:

1. queries NYC Open Data for the eight highest-volume complaint types;
2. retrieves daily aggregates for each category;
3. builds a complete category-date grid;
4. fills genuinely absent category-days with zero;
5. applies identical rolling-origin folds;
6. writes category-level fold and summary outputs;
7. validates complete coverage and forecast metrics.

To reduce stress on the public API, categories are now fetched as separate smaller aggregate queries instead of one expensive multi-category group query.

## Status

**Complete**

The next milestone will test whether category-specific seasonality and calendar features materially improve the volatile categories rather than assuming the citywide preferred model is optimal everywhere.
