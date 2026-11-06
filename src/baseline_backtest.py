import json
import math
from pathlib import Path

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
CONFIG = json.loads(
    (ROOT / "config" / "forecast.json").read_text(encoding="utf-8")
)


def metrics(actual, predicted):
    actual = np.asarray(actual, dtype=float)
    predicted = np.asarray(predicted, dtype=float)
    error = actual - predicted
    mae = float(np.mean(np.abs(error)))
    rmse = float(math.sqrt(np.mean(error ** 2)))
    denominator = float(np.sum(np.abs(actual)))
    wape = float(np.sum(np.abs(error)) / denominator)
    return {
        "mae": mae,
        "rmse": rmse,
        "wape": wape,
    }


def forecasts(train, horizon):
    last_value = float(train.iloc[-1])
    naive = np.repeat(last_value, horizon)

    if len(train) < 7:
        raise RuntimeError("Insufficient history for seasonal-naive forecast.")

    weekly_pattern = train.iloc[-7:].to_numpy(dtype=float)
    seasonal_naive = np.resize(weekly_pattern, horizon)

    rolling_window = min(28, len(train))
    rolling_mean = np.repeat(
        float(train.iloc[-rolling_window:].mean()),
        horizon,
    )

    return {
        "naive": naive,
        "seasonal_naive_7d": seasonal_naive,
        "rolling_mean_28d": rolling_mean,
    }


def main():
    source = ROOT / "data" / "raw" / "daily_requests.csv"
    if not source.exists():
        raise FileNotFoundError(
            "Run src/fetch_daily_counts.py before baseline backtesting."
        )

    frame = pd.read_csv(source, parse_dates=["date"])
    frame = frame.sort_values("date").reset_index(drop=True)

    horizon = CONFIG["forecast_horizon_days"]
    folds = CONFIG["backtest_folds"]
    step = CONFIG["backtest_step_days"]

    results = []

    for fold in range(folds):
        test_end = len(frame) - fold * step
        test_start = test_end - horizon

        if test_start <= 28:
            raise RuntimeError("Insufficient history for configured backtest.")

        train = frame.iloc[:test_start]["request_count"]
        test = frame.iloc[test_start:test_end]

        for model_name, prediction in forecasts(train, horizon).items():
            score = metrics(test["request_count"], prediction)
            results.append({
                "fold": folds - fold,
                "model": model_name,
                "train_end": frame.iloc[test_start - 1]["date"].date().isoformat(),
                "test_start": test.iloc[0]["date"].date().isoformat(),
                "test_end": test.iloc[-1]["date"].date().isoformat(),
                **score,
            })

    results_frame = pd.DataFrame(results).sort_values(
        ["fold", "model"]
    )

    summary = (
        results_frame.groupby("model")[["mae", "rmse", "wape"]]
        .mean()
        .sort_values("wape")
        .reset_index()
    )

    processed = ROOT / "data" / "processed"
    processed.mkdir(parents=True, exist_ok=True)
    results_frame.to_csv(processed / "baseline_folds.csv", index=False)
    summary.to_csv(processed / "baseline_summary.csv", index=False)

    print(summary.to_json(orient="records", indent=2))


if __name__ == "__main__":
    main()
