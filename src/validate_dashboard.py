import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
METADATA = ROOT / "data" / "metadata"
DASHBOARD = ROOT / "docs" / "dashboard.html"


def pct(value):
    return f"{value * 100:.1f}%"


def model_label(value):
    labels = {
        "rolling_mean_28d": "28-day rolling mean",
        "ets_weekly": "Weekly ETS",
        "hist_gradient_boosting": "HistGradientBoosting",
        "naive": "Naive",
        "seasonal_naive_7d": "7-day seasonal naive",
        "annual_naive_365d": "Annual naive (365d)",
        "calendar_lag_hgb": "Calendar/lag HGB",
    }
    return labels.get(value, value)


def main():
    if not DASHBOARD.exists():
        raise RuntimeError("Dashboard HTML is missing.")

    benchmark = json.loads(
        (METADATA / "benchmark_summary.json").read_text(encoding="utf-8")
    )
    categories = json.loads(
        (METADATA / "category_summary.json").read_text(encoding="utf-8")
    )
    operational = json.loads(
        (METADATA / "operational_forecast_summary.json").read_text(
            encoding="utf-8"
        )
    )
    targeted = json.loads(
        (METADATA / "targeted_category_summary.json").read_text(
            encoding="utf-8"
        )
    )
    html = DASHBOARD.read_text(encoding="utf-8")

    expected = [
        f'{operational["point_forecast_daily"]:,.0f}',
        pct(benchmark["preferred_metrics"]["wape"]),
        str(operational["fte_point"]),
        str(operational["fte_upper_80"]),
        str(operational["fte_upper_95"]),
        pct(categories["median_category_wape"]),
    ]

    for row in benchmark["ranking"]:
        expected.extend([model_label(row["model"]), pct(row["wape"])])

    for row in categories["categories"]:
        expected.extend([row["complaint_type"], pct(row["wape"])])

    for row in targeted["results"]:
        expected.extend([
            row["complaint_type"],
            pct(row["best_wape"]),
            pct(row["improvement_vs_rolling_mean"]),
        ])

    normalized_html = html.lower().replace("-", " ").replace("_", " ")
    missing = [
        value for value in expected
        if value.lower().replace("-", " ").replace("_", " ")
        not in normalized_html
    ]
    if missing:
        raise RuntimeError(
            "Dashboard is missing expected analytical values: "
            + ", ".join(missing)
        )

    print("Forecast dashboard semantic validation passed.")


if __name__ == "__main__":
    main()
