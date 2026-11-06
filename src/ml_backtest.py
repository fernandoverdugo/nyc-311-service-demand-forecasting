import json
import math
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.ensemble import HistGradientBoostingRegressor


ROOT = Path(__file__).resolve().parents[1]
CONFIG = json.loads(
    (ROOT / "config" / "forecast.json").read_text(encoding="utf-8")
)


FEATURES = [
    "lag_1",
    "lag_7",
    "lag_14",
    "lag_28",
    "rolling_mean_7",
    "rolling_mean_28",
    "day_of_week",
    "day_of_year_sin",
    "day_of_year_cos",
]


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


def feature_row(history, target_date):
    values = np.asarray(history, dtype=float)

    if len(values) < 28:
        raise RuntimeError("At least 28 days of history are required.")

    day_of_year = target_date.dayofyear
    angle = 2 * np.pi * day_of_year / 365.25

    return {
        "lag_1": float(values[-1]),
        "lag_7": float(values[-7]),
        "lag_14": float(values[-14]),
        "lag_28": float(values[-28]),
        "rolling_mean_7": float(values[-7:].mean()),
        "rolling_mean_28": float(values[-28:].mean()),
        "day_of_week": int(target_date.dayofweek),
        "day_of_year_sin": float(np.sin(angle)),
        "day_of_year_cos": float(np.cos(angle)),
    }


def supervised_frame(frame):
    rows = []

    for idx in range(28, len(frame)):
        row = feature_row(
            frame.iloc[:idx]["request_count"],
            frame.iloc[idx]["date"],
        )
        row["target"] = float(frame.iloc[idx]["request_count"])
        rows.append(row)

    return pd.DataFrame(rows)


def recursive_forecast(train_frame, future_dates):
    training = supervised_frame(train_frame)

    model = HistGradientBoostingRegressor(
        learning_rate=0.06,
        max_iter=250,
        max_leaf_nodes=15,
        l2_regularization=1.0,
        random_state=CONFIG["random_seed"],
    )
    model.fit(training[FEATURES], training["target"])

    history = train_frame["request_count"].astype(float).tolist()
    predictions = []

    for date in future_dates:
        row = pd.DataFrame(
            [feature_row(history, date)],
            columns=FEATURES,
        )
        prediction = float(model.predict(row)[0])
        prediction = max(0.0, prediction)
        predictions.append(prediction)
        history.append(prediction)

    return np.asarray(predictions)


def main():
    source = ROOT / "data" / "raw" / "daily_requests.csv"
    if not source.exists():
        raise FileNotFoundError(
            "Run src/fetch_daily_counts.py before ML backtesting."
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

        train = frame.iloc[:test_start].copy()
        test = frame.iloc[test_start:test_end].copy()

        prediction = recursive_forecast(
            train,
            test["date"].tolist(),
        )

        score = metrics(
            test["request_count"],
            prediction,
        )

        rows.append({
            "fold": folds - fold,
            "model": "hist_gradient_boosting",
            "train_end": train.iloc[-1]["date"].date().isoformat(),
            "test_start": test.iloc[0]["date"].date().isoformat(),
            "test_end": test.iloc[-1]["date"].date().isoformat(),
            **score,
        })

    result = pd.DataFrame(rows).sort_values("fold")
    processed = ROOT / "data" / "processed"
    processed.mkdir(parents=True, exist_ok=True)
    result.to_csv(
        processed / "ml_folds.csv",
        index=False,
    )

    summary = result[["mae", "rmse", "wape"]].mean()

    print(json.dumps({
        "model": "hist_gradient_boosting",
        "mae": float(summary["mae"]),
        "rmse": float(summary["rmse"]),
        "wape": float(summary["wape"]),
    }, indent=2))


if __name__ == "__main__":
    main()
