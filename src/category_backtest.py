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
    denominator = float(np.sum(np.abs(actual)))
    return {
        "mae": float(np.mean(np.abs(error))),
        "rmse": float(math.sqrt(np.mean(error ** 2))),
        "wape": (
            float(np.sum(np.abs(error)) / denominator)
            if denominator > 0
            else np.nan
        ),
    }


def rolling_mean_forecast(train, horizon):
    value = float(train.iloc[-28:].mean())
    return np.repeat(value, horizon)


def seasonal_naive_forecast(train, horizon):
    pattern = train.iloc[-7:].to_numpy(dtype=float)
    return np.resize(pattern, horizon)


def main():
    source = ROOT / "data" / "raw" / "daily_category_requests.csv"
    if not source.exists():
        raise FileNotFoundError(
            "Run src/fetch_category_counts.py before category backtesting."
        )

    frame = pd.read_csv(source, parse_dates=["date"])
    horizon = CONFIG["forecast_horizon_days"]
    folds = CONFIG["backtest_folds"]
    step = CONFIG["backtest_step_days"]

    rows = []

    for category, group in frame.groupby("complaint_type"):
        group = group.sort_values("date").reset_index(drop=True)

        for fold in range(folds):
            test_end = len(group) - fold * step
            test_start = test_end - horizon
            train = group.iloc[:test_start]["request_count"]
            test = group.iloc[test_start:test_end]

            models = {
                "rolling_mean_28d": rolling_mean_forecast(
                    train,
                    horizon,
                ),
                "seasonal_naive_7d": seasonal_naive_forecast(
                    train,
                    horizon,
                ),
            }

            for model, prediction in models.items():
                score = metrics(
                    test["request_count"],
                    prediction,
                )
                rows.append({
                    "complaint_type": category,
                    "fold": folds - fold,
                    "model": model,
                    "train_end": (
                        group.iloc[test_start - 1]["date"]
                        .date()
                        .isoformat()
                    ),
                    "test_start": test.iloc[0]["date"].date().isoformat(),
                    "test_end": test.iloc[-1]["date"].date().isoformat(),
                    **score,
                })

    results = pd.DataFrame(rows)
    summary = (
        results.groupby(["complaint_type", "model"])[
            ["mae", "rmse", "wape"]
        ]
        .mean()
        .reset_index()
    )

    volume = (
        frame.groupby("complaint_type")["request_count"]
        .sum()
        .rename("total_requests")
        .reset_index()
    )

    summary = summary.merge(
        volume,
        on="complaint_type",
        how="left",
    )

    processed = ROOT / "data" / "processed"
    processed.mkdir(parents=True, exist_ok=True)
    results.to_csv(
        processed / "category_folds.csv",
        index=False,
    )
    summary.to_csv(
        processed / "category_summary.csv",
        index=False,
    )

    preferred = (
        summary[summary["model"] == "rolling_mean_28d"]
        .sort_values("wape")
        .reset_index(drop=True)
    )

    payload = {
        "category_count": int(preferred["complaint_type"].nunique()),
        "most_predictable": preferred.head(3).to_dict(
            orient="records"
        ),
        "least_predictable": preferred.tail(3).sort_values(
            "wape",
            ascending=False,
        ).to_dict(orient="records"),
    }

    print(json.dumps(payload, indent=2))


if __name__ == "__main__":
    main()
