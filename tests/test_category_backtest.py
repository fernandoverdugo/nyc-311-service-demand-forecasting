import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from category_backtest import (
    rolling_mean_forecast,
    seasonal_naive_forecast,
)


def test_category_rolling_mean_forecast_horizon():
    train = pd.Series(range(1, 40))
    result = rolling_mean_forecast(train, 9)
    assert len(result) == 9


def test_category_seasonal_naive_repeats_week():
    train = pd.Series(range(1, 15))
    result = seasonal_naive_forecast(train, 10)
    assert result.tolist() == [8, 9, 10, 11, 12, 13, 14, 8, 9, 10]
