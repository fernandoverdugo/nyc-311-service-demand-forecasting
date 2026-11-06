import json
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]


def main():
    processed = ROOT / "data" / "processed"
    baseline = pd.read_csv(processed / "baseline_folds.csv")
    ets = pd.read_csv(processed / "ets_folds.csv")

    combined = pd.concat(
        [baseline, ets],
        ignore_index=True,
    )

    summary = (
        combined.groupby("model")[["mae", "rmse", "wape"]]
        .agg(["mean", "std"])
    )
    summary.columns = [
        f"{metric}_{stat}"
        for metric, stat in summary.columns
    ]
    summary = (
        summary.reset_index()
        .sort_values("wape_mean")
        .reset_index(drop=True)
    )
    summary["wape_improvement_vs_seasonal_naive"] = (
        1
        - summary["wape_mean"]
        / float(
            summary.loc[
                summary["model"] == "seasonal_naive_7d",
                "wape_mean",
            ].iloc[0]
        )
    )

    summary.to_csv(
        processed / "model_comparison.csv",
        index=False,
    )

    payload = {
        "models": summary.to_dict(orient="records"),
        "best_model": str(summary.iloc[0]["model"]),
        "best_wape": float(summary.iloc[0]["wape_mean"]),
    }

    print(json.dumps(payload, indent=2))


if __name__ == "__main__":
    main()
