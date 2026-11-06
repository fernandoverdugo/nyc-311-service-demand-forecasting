import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from operational_forecast import (
    rolling_mean_forecast,
    staffing_required,
)


def test_rolling_mean_forecast_is_constant():
    train = pd.Series(range(1, 40))
    result = rolling_mean_forecast(train, 5)
    assert len(result) == 5
    assert len(set(result.tolist())) == 1


def test_staffing_rounds_up():
    assert staffing_required(1) == 1
    assert staffing_required(100) >= 3
