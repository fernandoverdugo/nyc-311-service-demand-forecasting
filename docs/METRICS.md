# Forecasting Metrics & Terms

This glossary explains the main forecasting and operational-planning terms used in the project.

## WAPE

**Weighted Absolute Percentage Error (WAPE)** measures total absolute forecast error relative to total observed demand.

Lower values indicate better forecast accuracy.

A WAPE of 7.3% means the model's total absolute error is about 7.3% of the observed demand over the evaluation period.

WAPE is the project's primary model-selection metric because it is easy to interpret for aggregate operational volume.

## MAE

**Mean Absolute Error (MAE)** is the average absolute difference between predicted and observed daily request counts.

MAE remains in the original unit of the target: requests per day.

## RMSE

**Root Mean Squared Error (RMSE)** also measures forecast error in requests per day, but penalizes larger misses more heavily than MAE.

## Rolling-origin validation

**Rolling-origin backtesting** evaluates forecasts at multiple historical points in time.

For each fold, the model trains only on data available before the forecast origin and predicts the following 28 days. This preserves temporal ordering and reduces look-ahead leakage.

## Forecast horizon

The **forecast horizon** is how far into the future the model predicts.

This project uses a 28-day operational horizon.

## Naive forecast

A **naive forecast** uses the most recent observed level as the future prediction.

It is an important benchmark because a more complex model should outperform a simple baseline to justify its added complexity.

## Seasonal naive forecast

A **seasonal naive forecast** repeats a prior seasonal pattern.

The project evaluates a 7-day seasonal naive model and, for targeted categories, a 365-day annual naive model.

## Exponential smoothing / ETS

**ETS** models represent level, trend, and seasonality through exponential smoothing.

The citywide benchmark includes a weekly ETS model as a statistical forecasting challenger.

## Lag features

**Lag features** use earlier observations of the target as predictors, such as demand 1, 7, 14, 28, or 365 days earlier.

The targeted machine-learning models combine lag features with calendar information.

## Prediction / planning bands

The dashboard's **80% and 95% planning bands** are empirical ranges based on historical rolling-origin forecast errors.

They are operational planning ranges, not parametric confidence intervals.

## FTE

**FTE** means **full-time equivalent**.

The staffing figures in the dashboard convert forecast demand into an illustrative FTE requirement using explicit assumptions about requests handled per FTE per day and target utilization.

These are scenario assumptions for demonstrating workload translation; they are not NYC staffing standards.

## Target utilization

**Target utilization** is the share of theoretical staff capacity assumed to be safely usable for planning.

The default scenario uses 85% utilization to leave room for normal operational variability.

## Category forecastability

**Category forecastability** describes how accurately individual complaint types can be predicted.

The project shows that citywide aggregate demand is much easier to forecast than many individual service categories.

## Model selection principle

The project does not assume that more complex models are better.

The preferred model is the one that performs best under out-of-time validation while remaining appropriate for the behavior of the series.
