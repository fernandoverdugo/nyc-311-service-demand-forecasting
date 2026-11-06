import json
import math
from pathlib import Path

import numpy as np
import pandas as pd
from statsmodels.tsa.holtwinters import ExponentialSmoothing


ROOT = Path(__file__).resolve().parents[1]
CONFIG = json.loads(
    (ROOT / "config" / "forecast.json").read_text(encoding="utf-8")
)


def metrics(actual, predicted):
    actual = np.asarray(actual, dtype=float)
    predicted = np.asarray(predicted, dtype=float)
    error = actual - predicted
    return {
        "mae": float(np.mean(np.abs(error))),
        "rmse": float(math.sqrt(np.mean(error ** 2))),
        "wape": float(
            np.sum(np.abs(error)) / np.sum(np.abs(actual))
        ),
    }


def fit_ets(train, horizon):
    model = ExponentialSmoothing(
        train.to_numpy(dtype=float),
        trend="add",
        damped_trend=True,
        seasonal="add",
        seasonal_periods=7,
        initialization_method="estimated",
    )
    fitted = model.fit(optimized=True, use_brute=False)
    forecast = fitted.forecast(horizon)
    return np.asarray(forecast, dtype=float)


def main():
    source = ROOT / "data" / "raw" / "daily_requests.csv"
    if not source.exists():
        raise FileNotFoundError(
            "Run src/fetch_daily_counts.py before statistical backtesting."
        )

    frame = pd.read_csv(source, parse_dates=["date"])
    frame = frame.sort_values("date").reset_index(drop=True)

    horizon = CONFIG["forecast_horizon_days"]
    folds = CONFIG["backtest_folds"]
    step = CONFIG["backtest_step_days"]

    rows = []

    for fold in range(folds):
        test_end = len(frame) - fold * step
        test_start = test_end - horizon

        train = frame.iloc[:test_start]["request_count"]
        test = frame.iloc[test_start:test_end]

        prediction = fit_ets(train, horizon)
        score = metrics(test["request_count"], prediction)

        rows.append({
            "fold": folds - fold,
            "model": "ets_weekly",
            "train_end": frame.iloc[test_start - 1]["date"].date().isoformat(),
            "test_start": test.iloc[0]["date"].date().isoformat(),
            "test_end": test.iloc[-1]["date"].date().isoformat(),
            **score,
        })

    result = pd.DataFrame(rows).sort_values("fold")
    summary = result[["mae", "rmse", "wape"]].mean().to_dict()

    processed = ROOT / "data" / "processed"
    processed.mkdir(parents=True, exist_ok=True)
    result.to_csv(processed / "ets_folds.csv", index=False)

    print(json.dumps({
        "model": "ets_weekly",
        **{key: float(value) for key, value in summary.items()},
    }, indent=2))


if __name__ == "__main__":
    main()
