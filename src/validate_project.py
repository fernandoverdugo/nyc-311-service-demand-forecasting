import json
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
CONFIG = json.loads(
    (ROOT / "config" / "forecast.json").read_text(encoding="utf-8")
)


def main():
    source = ROOT / "data" / "raw" / "daily_requests.csv"
    folds = ROOT / "data" / "processed" / "baseline_folds.csv"
    summary = ROOT / "data" / "processed" / "baseline_summary.csv"
    operational = ROOT / "data" / "processed" / "operational_forecast.csv"
    operational_summary = (
        ROOT / "data" / "processed" / "operational_forecast_summary.json"
    )

    for path in [
        source,
        folds,
        summary,
        operational,
        operational_summary,
    ]:
        if not path.exists():
            raise RuntimeError(f"Missing required artifact: {path}")

    daily = pd.read_csv(source, parse_dates=["date"])
    results = pd.read_csv(folds)
    baseline = pd.read_csv(summary)
    forecast = pd.read_csv(operational)

    expected_days = len(
        pd.date_range(
            CONFIG["analysis_start"],
            CONFIG["analysis_end"],
            freq="D",
        )
    )

    if len(daily) != expected_days:
        raise RuntimeError("Daily series length does not match config.")

    if daily["date"].duplicated().any():
        raise RuntimeError("Daily series contains duplicate dates.")

    if (daily["request_count"] <= 0).any():
        raise RuntimeError("Daily request counts must be positive.")

    expected_rows = CONFIG["backtest_folds"] * 3
    if len(results) != expected_rows:
        raise RuntimeError("Unexpected number of baseline fold results.")

    if set(baseline["model"]) != {
        "naive",
        "seasonal_naive_7d",
        "rolling_mean_28d",
    }:
        raise RuntimeError("Baseline model set does not match contract.")

    if not baseline["wape"].between(0, 1).all():
        raise RuntimeError("Invalid WAPE values.")

    if len(forecast) != CONFIG["forecast_horizon_days"]:
        raise RuntimeError("Operational forecast horizon mismatch.")

    interval_columns = [
        "lower_80",
        "point_forecast",
        "upper_80",
        "lower_95",
        "upper_95",
    ]
    if forecast[interval_columns].isna().any().any():
        raise RuntimeError("Operational forecast contains missing intervals.")

    if not (
        (forecast["lower_95"] <= forecast["lower_80"])
        & (forecast["lower_80"] <= forecast["point_forecast"])
        & (forecast["point_forecast"] <= forecast["upper_80"])
        & (forecast["upper_80"] <= forecast["upper_95"])
    ).all():
        raise RuntimeError("Forecast interval ordering is invalid.")

    if not (
        (forecast["fte_point"] <= forecast["fte_upper_80"])
        & (forecast["fte_upper_80"] <= forecast["fte_upper_95"])
    ).all():
        raise RuntimeError("Staffing interval ordering is invalid.")

    print("NYC 311 forecasting validation passed.")


if __name__ == "__main__":
    main()
