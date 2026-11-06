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

    for path in [source, folds, summary]:
        if not path.exists():
            raise RuntimeError(f"Missing required artifact: {path}")

    daily = pd.read_csv(source, parse_dates=["date"])
    results = pd.read_csv(folds)
    baseline = pd.read_csv(summary)

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

    print("NYC 311 forecasting foundation validation passed.")


if __name__ == "__main__":
    main()
