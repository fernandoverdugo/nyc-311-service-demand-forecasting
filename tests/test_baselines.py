import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from baseline_backtest import forecasts, metrics


def test_metrics_are_zero_for_perfect_forecast():
    actual = np.array([10, 20, 30])
    result = metrics(actual, actual)
    assert result["mae"] == 0
    assert result["rmse"] == 0
    assert result["wape"] == 0


def test_seasonal_naive_repeats_last_week():
    train = pd.Series(range(1, 15))
    result = forecasts(train, 10)["seasonal_naive_7d"]
    assert result.tolist() == [8, 9, 10, 11, 12, 13, 14, 8, 9, 10]
