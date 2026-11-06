import json
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
CONFIG = json.loads(
    (ROOT / "config" / "forecast.json").read_text(encoding="utf-8")
)


def build_url():
    select = "date_trunc_ymd(created_date) as date, count(*) as request_count"
    where = (
        f"created_date >= '{CONFIG['analysis_start']}T00:00:00.000' "
        f"AND created_date < '2026-10-01T00:00:00.000'"
    )
    params = {
        "$select": select,
        "$where": where,
        "$group": "date",
        "$order": "date",
        "$limit": 5000,
    }
    return CONFIG["api_base"] + "?" + urllib.parse.urlencode(params)


def fetch_payload(url, attempts=5):
    request = urllib.request.Request(
        url,
        headers={"User-Agent": "nyc-311-demand-forecasting/1.0"},
    )

    for attempt in range(1, attempts + 1):
        try:
            with urllib.request.urlopen(
                request,
                timeout=60,
            ) as response:
                return json.loads(
                    response.read().decode("utf-8")
                )
        except urllib.error.HTTPError as error:
            if error.code not in {429, 500, 502, 503, 504}:
                raise
            if attempt == attempts:
                raise
        except (urllib.error.URLError, TimeoutError):
            if attempt == attempts:
                raise

        time.sleep(2 ** (attempt - 1))

    raise RuntimeError("NYC Open Data request failed after retries.")


def main():
    url = build_url()
    payload = fetch_payload(url)

    frame = pd.DataFrame(payload)
    if frame.empty:
        raise RuntimeError("NYC Open Data returned no daily observations.")

    frame["date"] = pd.to_datetime(frame["date"]).dt.date
    frame["request_count"] = pd.to_numeric(
        frame["request_count"],
        errors="raise",
    ).astype(int)

    full_dates = pd.date_range(
        CONFIG["analysis_start"],
        CONFIG["analysis_end"],
        freq="D",
    )

    frame["date"] = pd.to_datetime(frame["date"])
    frame = (
        frame.set_index("date")
        .reindex(full_dates)
        .rename_axis("date")
        .reset_index()
    )

    if frame["request_count"].isna().any():
        missing = frame.loc[
            frame["request_count"].isna(),
            "date",
        ].dt.strftime("%Y-%m-%d").tolist()
        raise RuntimeError(
            "Missing dates in aggregated API response: "
            + ", ".join(missing[:10])
        )

    output = ROOT / "data" / "raw"
    output.mkdir(parents=True, exist_ok=True)
    frame.to_csv(output / "daily_requests.csv", index=False)

    summary = {
        "dataset_id": CONFIG["dataset_id"],
        "analysis_start": CONFIG["analysis_start"],
        "analysis_end": CONFIG["analysis_end"],
        "days": int(len(frame)),
        "total_requests": int(frame["request_count"].sum()),
        "mean_daily_requests": float(frame["request_count"].mean()),
        "min_daily_requests": int(frame["request_count"].min()),
        "max_daily_requests": int(frame["request_count"].max()),
    }

    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
