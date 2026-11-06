import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
METADATA = ROOT / "data" / "metadata"
DOCS = ROOT / "docs"


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


def bar(value, maximum):
    width = 0 if maximum <= 0 else min(100, value / maximum * 100)
    return (
        '<div class="bar"><span style="width:'
        f'{width:.1f}%"></span></div>'
    )


def main():
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

    ranking = benchmark["ranking"]
    max_model_wape = max(row["wape"] for row in ranking)
    model_rows = "".join(
        f"""
        <tr>
          <td>{model_label(row["model"])}</td>
          <td>{pct(row["wape"])}</td>
          <td>{bar(row["wape"], max_model_wape)}</td>
        </tr>
        """
        for row in ranking
    )

    category_rows = "".join(
        f"""
        <tr>
          <td>{row["complaint_type"]}</td>
          <td>{row["total_requests"]:,}</td>
          <td>{pct(row["wape"])}</td>
        </tr>
        """
        for row in categories["categories"]
    )

    targeted_rows = "".join(
        f"""
        <tr>
          <td>{row["complaint_type"]}</td>
          <td>{pct(row["baseline_wape"])}</td>
          <td>{model_label(row["best_model"])}</td>
          <td>{pct(row["best_wape"])}</td>
          <td><strong>{pct(row["improvement_vs_rolling_mean"])}</strong></td>
        </tr>
        """
        for row in targeted["results"]
    )

    point = operational["point_forecast_daily"]
    lower80 = max(0, point - operational["interval_half_width_80"])
    upper80 = point + operational["interval_half_width_80"]
    lower95 = max(0, point - operational["interval_half_width_95"])
    upper95 = point + operational["interval_half_width_95"]

    html = f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>NYC 311 Service Demand Forecasting Dashboard</title>
<style>
:root {{
  --bg:#f6f7f9;
  --card:#ffffff;
  --text:#17202a;
  --muted:#667085;
  --line:#e4e7ec;
  --accent:#2457d6;
  --accent2:#79a4ff;
  --good:#157347;
}}
* {{ box-sizing:border-box; }}
body {{
  margin:0;
  font-family:Inter,ui-sans-serif,system-ui,-apple-system,BlinkMacSystemFont,
    "Segoe UI",sans-serif;
  background:var(--bg);
  color:var(--text);
}}
main {{ max-width:1180px; margin:0 auto; padding:40px 24px 64px; }}
h1 {{ margin:0; font-size:34px; }}
.subtitle {{ color:var(--muted); margin:8px 0 28px; line-height:1.5; }}
.grid {{ display:grid; gap:16px; }}
.kpis {{ grid-template-columns:repeat(4,1fr); }}
.two {{ grid-template-columns:1fr 1fr; }}
.card {{
  background:var(--card);
  border:1px solid var(--line);
  border-radius:14px;
  padding:20px;
  box-shadow:0 1px 2px rgba(16,24,40,.04);
}}
.kpi-label {{
  color:var(--muted);
  font-size:13px;
  text-transform:uppercase;
  letter-spacing:.04em;
}}
.kpi-value {{ font-size:30px; font-weight:700; margin-top:6px; }}
.section {{ margin-top:22px; }}
h2 {{ margin:0 0 16px; font-size:20px; }}
h3 {{ margin:0 0 8px; font-size:15px; }}
.note {{ color:var(--muted); font-size:13px; line-height:1.5; }}
table {{ width:100%; border-collapse:collapse; font-size:14px; }}
th,td {{ padding:11px 9px; border-bottom:1px solid var(--line); text-align:left; }}
th {{ color:var(--muted); font-weight:600; }}
.bar {{ height:9px; min-width:100px; background:#edf0f5; border-radius:999px; overflow:hidden; }}
.bar span {{
  display:block;
  height:100%;
  background:linear-gradient(90deg,var(--accent),var(--accent2));
}}
.interval {{
  display:grid;
  grid-template-columns:repeat(3,1fr);
  gap:12px;
}}
.interval-item {{
  padding:14px;
  border:1px solid var(--line);
  border-radius:10px;
}}
.interval-item strong {{ display:block; font-size:22px; margin-top:4px; }}
.callout {{
  border-left:4px solid var(--accent);
  padding:14px 16px;
  background:#f8faff;
  border-radius:8px;
  line-height:1.55;
}}
.good {{ color:var(--good); }}
@media (max-width:850px) {{
  .kpis,.two {{ grid-template-columns:1fr 1fr; }}
}}
@media (max-width:620px) {{
  .kpis,.two,.interval {{ grid-template-columns:1fr; }}
  main {{ padding:28px 16px 48px; }}
  table {{ font-size:12px; }}
}}
</style>
</head>
<body>
<main>
  <h1>NYC 311 Service Demand Forecasting</h1>
  <p class="subtitle">
    Stakeholder forecast dashboard • fixed benchmark window
    {benchmark["data"]["analysis_start"]} through {benchmark["data"]["analysis_end"]}
    • 28-day planning horizon
  </p>

  <div class="grid kpis">
    <div class="card">
      <div class="kpi-label">Forecast demand</div>
      <div class="kpi-value">{point:,.0f}</div>
      <div class="note">requests per day</div>
    </div>
    <div class="card">
      <div class="kpi-label">Preferred model WAPE</div>
      <div class="kpi-value">{pct(benchmark["preferred_metrics"]["wape"])}</div>
      <div class="note">{model_label(benchmark["preferred_model"])}</div>
    </div>
    <div class="card">
      <div class="kpi-label">Illustrative staffing</div>
      <div class="kpi-value">{operational["fte_point"]}</div>
      <div class="note">FTE at point forecast</div>
    </div>
    <div class="card">
      <div class="kpi-label">Category median WAPE</div>
      <div class="kpi-value">{pct(categories["median_category_wape"])}</div>
      <div class="note">8 high-volume complaint types</div>
    </div>
  </div>

  <div class="grid two section">
    <section class="card">
      <h2>Planning uncertainty</h2>
      <div class="interval">
        <div class="interval-item">
          <span class="note">Point</span>
          <strong>{point:,.0f}</strong>
          <span class="note">requests/day</span>
        </div>
        <div class="interval-item">
          <span class="note">80% planning band</span>
          <strong>{lower80:,.0f}–{upper80:,.0f}</strong>
          <span class="note">{operational["fte_upper_80"]} FTE at upper band</span>
        </div>
        <div class="interval-item">
          <span class="note">95% planning band</span>
          <strong>{lower95:,.0f}–{upper95:,.0f}</strong>
          <span class="note">{operational["fte_upper_95"]} FTE at upper band</span>
        </div>
      </div>
      <p class="note">
        Bands are empirical planning ranges based on rolling-origin backtest
        errors, not parametric confidence intervals.
      </p>
    </section>

    <section class="card">
      <h2>Operational interpretation</h2>
      <div class="callout">
        Citywide daily demand is comparatively stable: the simple
        <strong>28-day rolling mean</strong> outperformed the more complex
        statistical and machine-learning benchmarks on mean out-of-time WAPE.
        Category-level demand is much less uniform, so service lines should be
        forecast using models matched to their behavior.
      </div>
      <p class="note">
        Staffing assumes {operational["staffing_assumptions"]["requests_per_fte_day"]}
        requests per FTE per day at
        {pct(operational["staffing_assumptions"]["target_utilization"])}
        target utilization. This is an illustrative scenario, not an NYC
        staffing standard.
      </p>
    </section>
  </div>

  <section class="card section">
    <h2>Citywide model comparison</h2>
    <table>
      <thead>
        <tr><th>Model</th><th>Mean WAPE</th><th>Relative error</th></tr>
      </thead>
      <tbody>{model_rows}</tbody>
    </table>
  </section>

  <section class="card section">
    <h2>Category forecastability</h2>
    <p class="note">
      The same 28-day rolling-mean benchmark is applied to the eight
      highest-volume complaint types. Lower WAPE indicates better forecast
      accuracy.
    </p>
    <table>
      <thead>
        <tr><th>Complaint type</th><th>Requests</th><th>Mean WAPE</th></tr>
      </thead>
      <tbody>{category_rows}</tbody>
    </table>
  </section>

  <section class="card section">
    <h2>Targeted model improvements</h2>
    <p class="note">
      Volatile categories were retested with annual persistence and
      calendar/lag machine learning rather than assuming the citywide model
      was optimal.
    </p>
    <table>
      <thead>
        <tr>
          <th>Complaint type</th>
          <th>Rolling mean</th>
          <th>Best model</th>
          <th>Best WAPE</th>
          <th>Improvement</th>
        </tr>
      </thead>
      <tbody>{targeted_rows}</tbody>
    </table>
  </section>

  <section class="card section">
    <h2>Decision takeaway</h2>
    <div class="callout">
      <strong>Use simple models where they work.</strong> Aggregate 311 demand
      is forecastable with a recent-level baseline, while volatile categories
      benefit from service-specific seasonal or lag/calendar models. Forecast
      uncertainty should be translated into planning ranges rather than a
      single staffing number.
    </div>
  </section>

  <p class="note section">
    Source: NYC Open Data, 311 Service Requests from 2020 to Present
    (dataset erm2-nwe9). Forecast benchmark uses a fixed historical analysis
    window for reproducibility.
    <br><br>
    <a href="https://github.com/fernandoverdugo/nyc-311-service-demand-forecasting">View repository</a>
    · <a href="https://github.com/fernandoverdugo/nyc-311-service-demand-forecasting/blob/main/docs/RESEARCH_DESIGN.md">Research design</a>
    · <a href="https://github.com/fernandoverdugo/nyc-311-service-demand-forecasting/blob/main/docs/METRICS.md">Metrics glossary</a>
  </p>
</main>
</body>
</html>
"""

    DOCS.mkdir(parents=True, exist_ok=True)
    (DOCS / "dashboard.html").write_text(html, encoding="utf-8")
    print("Dashboard generated: docs/dashboard.html")


if __name__ == "__main__":
    main()
