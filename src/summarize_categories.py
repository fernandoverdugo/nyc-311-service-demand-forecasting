import json
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
PROCESSED = ROOT / "data" / "processed"


def main():
    summary = pd.read_csv(PROCESSED / "category_summary.csv")
    preferred = (
        summary[summary["model"] == "rolling_mean_28d"]
        .sort_values(["wape", "total_requests"], ascending=[True, False])
        .reset_index(drop=True)
    )

    payload = {
        "category_count": int(preferred["complaint_type"].nunique()),
        "categories": preferred[
            [
                "complaint_type",
                "total_requests",
                "mae",
                "rmse",
                "wape",
            ]
        ].to_dict(orient="records"),
        "most_predictable": preferred.head(3)[
            ["complaint_type", "total_requests", "wape"]
        ].to_dict(orient="records"),
        "least_predictable": preferred.tail(3).sort_values(
            "wape",
            ascending=False,
        )[
            ["complaint_type", "total_requests", "wape"]
        ].to_dict(orient="records"),
        "median_category_wape": float(preferred["wape"].median()),
    }

    output = PROCESSED / "category_summary.json"
    output.write_text(
        json.dumps(payload, indent=2) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(payload, indent=2))


if __name__ == "__main__":
    main()
