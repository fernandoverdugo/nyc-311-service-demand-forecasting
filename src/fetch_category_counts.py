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


def top_categories(limit=8):
    select = "complaint_type, count(*) as request_count"
    where = (
        f"created_date >= '{CONFIG['analysis_start']}T00:00:00.000' "
        f"AND created_date < '2026-10-01T00:00:00.000' "
        "AND complaint_type IS NOT NULL"
    )
    params = {
        "$select": select,
        "$where": where,
        "$group": "complaint_type",
        "$order": "request_count DESC",
        "$limit": limit,
    }
    url = CONFIG["api_base"] + "?" + urllib.parse.urlencode(params)
    return fetch_payload(url)


def daily_category_counts(categories):
    rows = []

    for category in categories:
        escaped = category.replace("'", "''")
        select = (
            "date_trunc_ymd(created_date) as date, "
            "count(*) as request_count"
        )
        where = (
            f"created_date >= '{CONFIG['analysis_start']}T00:00:00.000' "
            f"AND created_date < '2026-10-01T00:00:00.000' "
            f"AND complaint_type = '{escaped}'"
        )
        params = {
            "$select": select,
            "$where": where,
            "$group": "date",
            "$order": "date",
            "$limit": 5000,
        }
        url = CONFIG["api_base"] + "?" + urllib.parse.urlencode(params)
        payload = fetch_payload(url)

        for row in payload:
            row["complaint_type"] = category
            rows.append(row)

    return rows

def main():
    top = top_categories()
    categories = [row["complaint_type"] for row in top]

    payload = daily_category_counts(categories)
    frame = pd.DataFrame(payload)

    if frame.empty:
        raise RuntimeError("No category-level observations returned.")

    frame["date"] = pd.to_datetime(frame["date"])
    frame["request_count"] = pd.to_numeric(
        frame["request_count"],
        errors="raise",
    ).astype(int)

    dates = pd.date_range(
        CONFIG["analysis_start"],
        CONFIG["analysis_end"],
        freq="D",
    )
    grid = pd.MultiIndex.from_product(
        [dates, categories],
        names=["date", "complaint_type"],
    ).to_frame(index=False)

    frame = (
        grid.merge(
            frame,
            on=["date", "complaint_type"],
            how="left",
        )
        .fillna({"request_count": 0})
        .sort_values(["complaint_type", "date"])
        .reset_index(drop=True)
    )
    frame["request_count"] = frame["request_count"].astype(int)

    output = ROOT / "data" / "raw"
    output.mkdir(parents=True, exist_ok=True)
    frame.to_csv(
        output / "daily_category_requests.csv",
        index=False,
    )

    summary = {
        "categories": categories,
        "category_count": len(categories),
        "rows": len(frame),
        "volume_by_category": (
            frame.groupby("complaint_type")["request_count"]
            .sum()
            .sort_values(ascending=False)
            .to_dict()
        ),
    }

    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
