import json
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
PROCESSED = ROOT / "data" / "processed"


def main():
    comparison = pd.read_csv(PROCESSED / "model_comparison.csv")
    baseline = pd.read_csv(PROCESSED / "baseline_folds.csv")
    ets = pd.read_csv(PROCESSED / "ets_folds.csv")
    ml = pd.read_csv(PROCESSED / "ml_folds.csv")

    folds = pd.concat([baseline, ets, ml], ignore_index=True)

    best = comparison.iloc[0]

    payload = {
        "preferred_model": str(best["model"]),
        "preferred_wape": float(best["wape_mean"]),
        "preferred_mae": float(best["mae_mean"]),
        "preferred_rmse": float(best["rmse_mean"]),
        "model_ranking": comparison.to_dict(orient="records"),
        "folds": folds.to_dict(orient="records"),
    }

    output = PROCESSED / "benchmark_summary.json"
    output.write_text(
        json.dumps(payload, indent=2) + "\n",
        encoding="utf-8",
    )

    print(json.dumps(payload, indent=2))


if __name__ == "__main__":
    main()
