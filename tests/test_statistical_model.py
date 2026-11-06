import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from statistical_backtest import fit_ets


def test_ets_returns_requested_horizon():
    values = (
        100
        + np.arange(70) * 0.2
        + np.tile([0, 3, 6, 9, 7, 4, 1], 10)
    )
    forecast = fit_ets(pd.Series(values), 14)
    assert len(forecast) == 14
    assert np.isfinite(forecast).all()
