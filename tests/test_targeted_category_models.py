import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from targeted_category_backtest import (
    annual_naive_forecast,
    calendar_ml_forecast,
    feature_row,
)


def test_annual_naive_uses_prior_year():
    train = pd.Series(np.arange(500))
    result = annual_naive_forecast(train, 5)
    assert result.tolist() == [135, 136, 137, 138, 139]


def test_feature_row_uses_annual_lag():
    history = pd.Series(np.arange(1, 367))
    row = feature_row(history, pd.Timestamp("2026-02-01"))
    assert row["lag_1"] == 366
    assert row["lag_365"] == 2


def test_calendar_ml_returns_horizon():
    dates = pd.date_range("2024-01-01", periods=500, freq="D")
    values = (
        200
        + 40 * np.sin(2 * np.pi * np.arange(500) / 365.25)
        + np.tile([0, 4, 7, 9, 8, 5, 2], 72)[:500]
    )
    frame = pd.DataFrame({
        "date": dates,
        "request_count": values,
    })
    future = pd.date_range(
        dates[-1] + pd.Timedelta(days=1),
        periods=7,
        freq="D",
    )
    prediction = calendar_ml_forecast(frame, future)
    assert len(prediction) == 7
    assert np.isfinite(prediction).all()
