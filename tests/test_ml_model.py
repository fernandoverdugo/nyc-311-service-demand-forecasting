import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from ml_backtest import feature_row, recursive_forecast


def test_feature_row_uses_only_prior_history():
    history = pd.Series(np.arange(1, 30))
    row = feature_row(history, pd.Timestamp("2026-01-01"))
    assert row["lag_1"] == 29
    assert row["lag_7"] == 23
    assert row["lag_28"] == 2


def test_recursive_forecast_returns_horizon():
    dates = pd.date_range("2025-01-01", periods=90, freq="D")
    values = 100 + np.arange(90) * 0.1 + np.tile(
        [0, 3, 5, 7, 6, 4, 1],
        13,
    )[:90]
    frame = pd.DataFrame({
        "date": dates,
        "request_count": values,
    })
    future = pd.date_range(
        dates[-1] + pd.Timedelta(days=1),
        periods=7,
        freq="D",
    )
    prediction = recursive_forecast(frame, future)
    assert len(prediction) == 7
    assert np.isfinite(prediction).all()
