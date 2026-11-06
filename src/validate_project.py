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
    category_metadata = (
        ROOT / "data" / "metadata" / "category_summary.json"
    )
    targeted_raw = (
        ROOT / "data" / "raw" / "daily_targeted_category_requests.csv"
    )
    targeted_folds = (
        ROOT / "data" / "processed" / "targeted_category_folds.csv"
    )
    targeted_summary = (
        ROOT / "data" / "processed" / "targeted_category_summary.csv"
    )
    targeted_json = (
        ROOT / "data" / "processed" / "targeted_category_summary.json"
    )
    dashboard = ROOT / "docs" / "dashboard.html"
    dashboard_builder = ROOT / "src" / "build_dashboard.py"
    dashboard_validator = ROOT / "src" / "validate_dashboard.py"
    milestone4 = ROOT / "docs" / "MILESTONE4_DASHBOARD.md"
    benchmark_validator = ROOT / "src" / "validate_committed_benchmarks.py"

    for path in [
        source,
        folds,
        summary,
        operational,
        operational_summary,
        category_metadata,
        targeted_raw,
        targeted_folds,
        targeted_summary,
        targeted_json,
        dashboard,
        dashboard_builder,
        dashboard_validator,
        milestone4,
        benchmark_validator,
    ]:
        if not path.exists():
            raise RuntimeError(f"Missing required artifact: {path}")

    daily = pd.read_csv(source, parse_dates=["date"])
    results = pd.read_csv(folds)
    baseline = pd.read_csv(summary)
    forecast = pd.read_csv(operational)
    category_reference = json.loads(
        category_metadata.read_text(encoding="utf-8")
    )
    targeted_daily = pd.read_csv(targeted_raw, parse_dates=["date"])
    targeted_results = pd.read_csv(targeted_folds)
    targeted_metrics = pd.read_csv(targeted_summary)

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

    if category_reference["category_count"] != 8:
        raise RuntimeError("Committed category benchmark should contain eight categories.")

    if targeted_daily["complaint_type"].nunique() != 3:
        raise RuntimeError("Expected three targeted category series.")

    if len(targeted_daily) != expected_days * 3:
        raise RuntimeError("Targeted category daily grid is incomplete.")

    if targeted_daily[["date", "complaint_type"]].duplicated().any():
        raise RuntimeError("Duplicate targeted category-date observations found.")

    if targeted_results["complaint_type"].nunique() != 3:
        raise RuntimeError("Expected three targeted volatile categories.")

    expected_targeted_rows = (
        3
        * CONFIG["backtest_folds"]
        * 3
    )
    if len(targeted_results) != expected_targeted_rows:
        raise RuntimeError("Unexpected targeted backtest row count.")

    expected_models = {
        "rolling_mean_28d",
        "annual_naive_365d",
        "calendar_lag_hgb",
    }
    if set(targeted_results["model"]) != expected_models:
        raise RuntimeError("Targeted model set does not match contract.")

    if targeted_metrics["wape_mean"].isna().any():
        raise RuntimeError("Targeted summary contains missing WAPE values.")

    if not targeted_metrics["wape_mean"].between(0, 2).all():
        raise RuntimeError("Targeted WAPE values are outside expected range.")

    print("NYC 311 forecasting validation passed.")


if __name__ == "__main__":
    main()
