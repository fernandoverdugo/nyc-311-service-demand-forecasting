import json
import math
from pathlib import Path

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
CONFIG = json.loads(
    (ROOT / "config" / "forecast.json").read_text(encoding="utf-8")
)


def rolling_mean_forecast(train, horizon):
    value = float(train.iloc[-28:].mean())
    return np.repeat(value, horizon)


def backtest_errors(frame):
    horizon = CONFIG["forecast_horizon_days"]
    folds = CONFIG["backtest_folds"]
    step = CONFIG["backtest_step_days"]

    rows = []

    for fold in range(folds):
        test_end = len(frame) - fold * step
        test_start = test_end - horizon

        train = frame.iloc[:test_start]["request_count"]
        test = frame.iloc[test_start:test_end].copy()
        prediction = rolling_mean_forecast(train, horizon)

        for date, actual, forecast in zip(
            test["date"],
            test["request_count"],
            prediction,
        ):
            rows.append({
                "fold": folds - fold,
                "date": date.date().isoformat(),
                "actual": float(actual),
                "forecast": float(forecast),
                "error": float(actual - forecast),
                "abs_error": float(abs(actual - forecast)),
            })

    return pd.DataFrame(rows)


def staffing_required(volume):
    requests_per_fte = CONFIG["staffing"]["requests_per_fte_day"]
    utilization = CONFIG["staffing"]["target_utilization"]
    effective_capacity = requests_per_fte * utilization
    return int(math.ceil(volume / effective_capacity))


def main():
    source = ROOT / "data" / "raw" / "daily_requests.csv"
    if not source.exists():
        raise FileNotFoundError(
            "Run src/fetch_daily_counts.py before preferred forecasting."
        )

    frame = pd.read_csv(source, parse_dates=["date"])
    frame = frame.sort_values("date").reset_index(drop=True)

    errors = backtest_errors(frame)
    q80 = float(errors["abs_error"].quantile(0.80))
    q95 = float(errors["abs_error"].quantile(0.95))

    horizon = CONFIG["forecast_horizon_days"]
    point = rolling_mean_forecast(
        frame["request_count"],
        horizon,
    )

    future_dates = pd.date_range(
        frame.iloc[-1]["date"] + pd.Timedelta(days=1),
        periods=horizon,
        freq="D",
    )

    forecast = pd.DataFrame({
        "date": future_dates,
        "point_forecast": point,
    })
    forecast["lower_80"] = np.maximum(
        0,
        forecast["point_forecast"] - q80,
    )
    forecast["upper_80"] = (
        forecast["point_forecast"] + q80
    )
    forecast["lower_95"] = np.maximum(
        0,
        forecast["point_forecast"] - q95,
    )
    forecast["upper_95"] = (
        forecast["point_forecast"] + q95
    )

    forecast["fte_point"] = forecast["point_forecast"].apply(
        staffing_required
    )
    forecast["fte_upper_80"] = forecast["upper_80"].apply(
        staffing_required
    )
    forecast["fte_upper_95"] = forecast["upper_95"].apply(
        staffing_required
    )

    processed = ROOT / "data" / "processed"
    processed.mkdir(parents=True, exist_ok=True)

    errors.to_csv(
        processed / "preferred_backtest_errors.csv",
        index=False,
    )
    forecast.to_csv(
        processed / "operational_forecast.csv",
        index=False,
    )

    payload = {
        "preferred_model": "rolling_mean_28d",
        "forecast_horizon_days": horizon,
        "point_forecast_daily": float(point[0]),
        "interval_half_width_80": q80,
        "interval_half_width_95": q95,
        "fte_point": int(forecast.iloc[0]["fte_point"]),
        "fte_upper_80": int(forecast.iloc[0]["fte_upper_80"]),
        "fte_upper_95": int(forecast.iloc[0]["fte_upper_95"]),
        "staffing_assumptions": CONFIG["staffing"],
    }

    (processed / "operational_forecast_summary.json").write_text(
        json.dumps(payload, indent=2) + "\n",
        encoding="utf-8",
    )

    print(json.dumps(payload, indent=2))


if __name__ == "__main__":
    main()
