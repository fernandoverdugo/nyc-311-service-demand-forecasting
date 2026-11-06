import json
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
PROCESSED = ROOT / "data" / "processed"


def main():
    frame = pd.read_csv(
        PROCESSED / "targeted_category_summary.csv"
    )

    results = []

    for category, group in frame.groupby("complaint_type"):
        ranked = group.sort_values("wape_mean").reset_index(drop=True)
        baseline = float(
            ranked.loc[
                ranked["model"] == "rolling_mean_28d",
                "wape_mean",
            ].iloc[0]
        )
        best = ranked.iloc[0]

        results.append({
            "complaint_type": category,
            "best_model": str(best["model"]),
            "best_wape": float(best["wape_mean"]),
            "baseline_wape": baseline,
            "improvement_vs_rolling_mean": float(
                1 - best["wape_mean"] / baseline
            ),
            "all_models": ranked[
                [
                    "model",
                    "mae_mean",
                    "rmse_mean",
                    "wape_mean",
                    "wape_std",
                ]
            ].to_dict(orient="records"),
        })

    payload = {
        "target_category_count": len(results),
        "results": results,
    }

    (PROCESSED / "targeted_category_summary.json").write_text(
        json.dumps(payload, indent=2) + "\n",
        encoding="utf-8",
    )

    print(json.dumps(payload, indent=2))


if __name__ == "__main__":
    main()
