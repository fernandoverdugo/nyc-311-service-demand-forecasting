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

TARGET_CATEGORIES = [
    "HEAT/HOT WATER",
    "Noise - Street/Sidewalk",
    "Street Condition",
]

FEATURES = [
    "lag_1",
    "lag_7",
    "lag_14",
    "lag_28",
    "lag_365",
    "rolling_mean_7",
    "rolling_mean_28",
    "rolling_mean_90",
    "day_of_week",
    "is_weekend",
    "day_of_year_sin",
    "day_of_year_cos",
]


def metrics(actual, predicted):
    actual = np.asarray(actual, dtype=float)
    predicted = np.asarray(predicted, dtype=float)
    error = actual - predicted
    denominator = float(np.sum(np.abs(actual)))
    return {
        "mae": float(np.mean(np.abs(error))),
        "rmse": float(math.sqrt(np.mean(error ** 2))),
        "wape": float(
            np.sum(np.abs(error)) / denominator
        ) if denominator > 0 else np.nan,
    }


def rolling_mean_forecast(train, horizon):
    value = float(train.iloc[-28:].mean())
    return np.repeat(value, horizon)


def annual_naive_forecast(train, horizon):
    if len(train) < 365 + horizon:
        raise RuntimeError("Insufficient history for annual naive forecast.")
    values = train.to_numpy(dtype=float)
    start = len(values) - 365
    return values[start:start + horizon]


def feature_row(history, target_date):
    values = np.asarray(history, dtype=float)
    if len(values) < 365:
        raise RuntimeError("At least 365 days of history are required.")

    angle = 2 * np.pi * target_date.dayofyear / 365.25

    return {
        "lag_1": float(values[-1]),
        "lag_7": float(values[-7]),
        "lag_14": float(values[-14]),
        "lag_28": float(values[-28]),
        "lag_365": float(values[-365]),
        "rolling_mean_7": float(values[-7:].mean()),
        "rolling_mean_28": float(values[-28:].mean()),
        "rolling_mean_90": float(values[-90:].mean()),
        "day_of_week": int(target_date.dayofweek),
        "is_weekend": int(target_date.dayofweek >= 5),
        "day_of_year_sin": float(np.sin(angle)),
        "day_of_year_cos": float(np.cos(angle)),
    }


def supervised_frame(frame):
    rows = []

    for idx in range(365, len(frame)):
        row = feature_row(
            frame.iloc[:idx]["request_count"],
            frame.iloc[idx]["date"],
        )
        row["target"] = float(frame.iloc[idx]["request_count"])
        rows.append(row)

    return pd.DataFrame(rows)


def calendar_ml_forecast(train_frame, future_dates):
    training = supervised_frame(train_frame)

    model = HistGradientBoostingRegressor(
        learning_rate=0.05,
        max_iter=300,
        max_leaf_nodes=15,
        l2_regularization=2.0,
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
        prediction = max(0.0, float(model.predict(row)[0]))
        predictions.append(prediction)
        history.append(prediction)

    return np.asarray(predictions)


def main():
    source = ROOT / "data" / "raw" / "daily_targeted_category_requests.csv"
    if not source.exists():
        raise FileNotFoundError(
            "Run src/fetch_category_counts.py before targeted backtesting."
        )

    frame = pd.read_csv(source, parse_dates=["date"])
    horizon = CONFIG["forecast_horizon_days"]
    folds = CONFIG["backtest_folds"]
    step = CONFIG["backtest_step_days"]

    rows = []

    for category in TARGET_CATEGORIES:
        group = (
            frame[frame["complaint_type"] == category]
            .sort_values("date")
            .reset_index(drop=True)
        )

        if group.empty:
            raise RuntimeError(f"Missing target category: {category}")

        for fold in range(folds):
            test_end = len(group) - fold * step
            test_start = test_end - horizon

            train_frame = group.iloc[:test_start].copy()
            train = train_frame["request_count"]
            test = group.iloc[test_start:test_end].copy()

            models = {
                "rolling_mean_28d": rolling_mean_forecast(
                    train,
                    horizon,
                ),
                "annual_naive_365d": annual_naive_forecast(
                    train,
                    horizon,
                ),
                "calendar_lag_hgb": calendar_ml_forecast(
                    train_frame,
                    test["date"].tolist(),
                ),
            }

            for model_name, prediction in models.items():
                score = metrics(
                    test["request_count"],
                    prediction,
                )
                rows.append({
                    "complaint_type": category,
                    "fold": folds - fold,
                    "model": model_name,
                    "train_end": (
                        train_frame.iloc[-1]["date"]
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
        .agg(["mean", "std"])
    )
    summary.columns = [
        f"{metric}_{stat}"
        for metric, stat in summary.columns
    ]
    summary = summary.reset_index()

    processed = ROOT / "data" / "processed"
    processed.mkdir(parents=True, exist_ok=True)
    results.to_csv(
        processed / "targeted_category_folds.csv",
        index=False,
    )
    summary.to_csv(
        processed / "targeted_category_summary.csv",
        index=False,
    )

    best = (
        summary.sort_values(
            ["complaint_type", "wape_mean"],
        )
        .groupby("complaint_type", as_index=False)
        .first()
    )

    print(json.dumps({
        "best_models": best.to_dict(orient="records"),
    }, indent=2))


if __name__ == "__main__":
    main()
