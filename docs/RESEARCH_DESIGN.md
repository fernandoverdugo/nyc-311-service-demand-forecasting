# Research Design

## Business problem

Municipal service organizations receive highly variable workloads. Forecasting expected service-request volume can help operations teams anticipate staffing pressure, schedule resources, and distinguish predictable seasonal variation from unusual demand.

## Primary analytical question

How accurately can daily NYC 311 service-request volume be forecast over a 28-day operational horizon?

## Secondary questions

1. How strong are weekly and annual seasonal patterns?
2. How much value does a seasonal-naive benchmark provide?
3. Do statistical forecasting models outperform simple operational baselines?
4. Do lag-feature machine-learning models improve forecast accuracy?
5. Which service-request categories are most predictable?
6. How wide should forecast uncertainty bands be?
7. How can forecast volume be translated into approximate workload or staffing requirements?

## Forecast target

Daily count of NYC 311 service requests.

## Validation design

Models are evaluated with rolling-origin backtesting. Every fold trains only on observations available before the forecast origin and predicts the following 28 days.

Primary metrics:

- MAE
- RMSE
- WAPE

Accuracy is compared against simple naive baselines before more complex models are considered.

## Reproducibility

The source dataset changes daily, so the benchmark window is fixed at 2022-01-01 through 2026-09-30.

## Responsible interpretation

Forecasts estimate aggregate operational demand. They are not designed to predict individual behavior, eligibility, enforcement activity, or outcomes for specific people.
