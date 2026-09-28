# Public Health Data Tracker

Pulls historical case data from the [disease.sh](https://disease.sh) public
API for a set of countries, processes it into a clean time series, and
plots trend and comparison charts. Falls back to a bundled offline
sample dataset automatically if there's no internet access, so the
project always runs end-to-end.

## Files
- `tracker.py` — fetch (or fallback), process, and chart
- `sample_covid_data.csv` — bundled offline sample dataset (8 countries, 180 days)
- `processed_covid_data.csv` — output: cleaned time series (generated on run)
- `chart_cumulative_cases.png`, `chart_total_cases_by_country.png` — output charts

## How to run
```bash
pip install pandas matplotlib requests
python tracker.py             # tries the live API, falls back automatically
python tracker.py --offline   # skip the API call entirely
```

## What it demonstrates
- Calling a **REST API** and handling failures gracefully (timeouts, HTTP
  errors) with a fallback data path — a real-world reliability pattern
- Turning cumulative API data into daily new-case counts
- Time-series aggregation and multi-series charting with `matplotlib`
- Simple CLI design with `argparse`

## Extending this project
- Swap in any other public API (exchange rates, weather, stock prices) —
  the fetch/fallback/process/chart pattern stays the same
- Add a 7-day rolling average column to smooth daily noise
- Deploy the charts as a simple Streamlit or Flask dashboard
