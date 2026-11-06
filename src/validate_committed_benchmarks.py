import json
import math
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PROCESSED = ROOT / "data" / "processed"
METADATA = ROOT / "data" / "metadata"


def load_json(path):
    return json.loads(path.read_text(encoding="utf-8"))


def assert_close(actual, expected, label, tolerance=1e-9):
    if not math.isclose(
        float(actual),
        float(expected),
        rel_tol=tolerance,
        abs_tol=tolerance,
    ):
        raise RuntimeError(
            f"{label} mismatch: regenerated={actual}, committed={expected}"
        )


def validate_benchmark():
    regenerated = load_json(PROCESSED / "benchmark_summary.json")
    committed = load_json(METADATA / "benchmark_summary.json")

    if regenerated["preferred_model"] != committed["preferred_model"]:
        raise RuntimeError("Preferred citywide model does not match committed benchmark.")

    assert_close(
        regenerated["preferred_wape"],
        committed["preferred_metrics"]["wape"],
        "Preferred WAPE",
    )
    assert_close(
        regenerated["preferred_mae"],
        committed["preferred_metrics"]["mae"],
        "Preferred MAE",
    )
    assert_close(
        regenerated["preferred_rmse"],
        committed["preferred_metrics"]["rmse"],
        "Preferred RMSE",
    )

    regenerated_wape = {
        row["model"]: row["wape_mean"]
        for row in regenerated["model_ranking"]
    }
    committed_wape = {
        row["model"]: row["wape"]
        for row in committed["ranking"]
    }

    if set(regenerated_wape) != set(committed_wape):
        raise RuntimeError("Citywide model set does not match committed benchmark.")

    for model, expected in committed_wape.items():
        assert_close(
            regenerated_wape[model],
            expected,
            f"{model} WAPE",
        )


def validate_operational():
    regenerated = load_json(
        PROCESSED / "operational_forecast_summary.json"
    )
    committed = load_json(
        METADATA / "operational_forecast_summary.json"
    )

    for key in [
        "preferred_model",
        "forecast_horizon_days",
        "fte_point",
        "fte_upper_80",
        "fte_upper_95",
    ]:
        if regenerated[key] != committed[key]:
            raise RuntimeError(
                f"Operational summary mismatch for {key}: "
                f"regenerated={regenerated[key]}, committed={committed[key]}"
            )

    for key in [
        "point_forecast_daily",
        "interval_half_width_80",
        "interval_half_width_95",
    ]:
        assert_close(
            regenerated[key],
            committed[key],
            f"Operational {key}",
        )


def validate_targeted():
    regenerated = load_json(
        PROCESSED / "targeted_category_summary.json"
    )
    committed = load_json(
        METADATA / "targeted_category_summary.json"
    )

    if regenerated["target_category_count"] != committed["target_category_count"]:
        raise RuntimeError("Targeted category count does not match committed benchmark.")

    regenerated_rows = {
        row["complaint_type"]: row
        for row in regenerated["results"]
    }
    committed_rows = {
        row["complaint_type"]: row
        for row in committed["results"]
    }

    if set(regenerated_rows) != set(committed_rows):
        raise RuntimeError("Targeted category set does not match committed benchmark.")

    for category, expected in committed_rows.items():
        actual = regenerated_rows[category]

        if actual["best_model"] != expected["best_model"]:
            raise RuntimeError(
                f"{category} best-model mismatch: "
                f"regenerated={actual['best_model']}, "
                f"committed={expected['best_model']}"
            )

        for key in [
            "best_wape",
            "baseline_wape",
            "improvement_vs_rolling_mean",
        ]:
            assert_close(
                actual[key],
                expected[key],
                f"{category} {key}",
            )


def main():
    validate_benchmark()
    validate_operational()
    validate_targeted()
    print("Committed forecast benchmark validation passed.")


if __name__ == "__main__":
    main()
