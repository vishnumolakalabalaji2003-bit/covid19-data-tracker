"""
Public Health Data Tracker (COVID-19 style)
--------------------------------------------
Pulls case data from a public API (disease.sh), falls back to a bundled
sample dataset if there's no internet connection, then produces trend
charts and a country comparison.

Run:
    python tracker.py                # tries live API first
    python tracker.py --offline      # forces use of sample_covid_data.csv
"""
import sys
import argparse
import pandas as pd
import matplotlib.pyplot as plt

API_URL = "https://disease.sh/v3/covid-19/historical"
COUNTRIES = ["USA", "India", "Brazil", "UK", "Germany", "France", "Japan", "Canada"]
SAMPLE_FILE = "sample_covid_data.csv"


def fetch_live(countries=COUNTRIES, days=180) -> pd.DataFrame:
    import requests
    rows = []
    for country in countries:
        resp = requests.get(f"{API_URL}/{country}", params={"lastdays": days}, timeout=10)
        resp.raise_for_status()
        data = resp.json()["timeline"]["cases"]
        prev = 0
        for date_str, cum_cases in data.items():
            new_cases = max(0, cum_cases - prev)
            prev = cum_cases
            rows.append([date_str, country, new_cases, cum_cases])
    df = pd.DataFrame(rows, columns=["date", "country", "new_cases", "cumulative_cases"])
    df["date"] = pd.to_datetime(df["date"], format="%m/%d/%y")
    return df


def load_offline() -> pd.DataFrame:
    df = pd.read_csv(SAMPLE_FILE)
    df["date"] = pd.to_datetime(df["date"])
    return df


def get_data(force_offline: bool) -> pd.DataFrame:
    if force_offline:
        print("Using offline sample dataset.")
        return load_offline()
    try:
        print("Attempting to fetch live data from disease.sh ...")
        return fetch_live()
    except Exception as e:
        print(f"Live fetch failed ({e}); falling back to offline sample dataset.")
        return load_offline()


def make_charts(df: pd.DataFrame):
    # Chart 1: cumulative cases over time, one line per country
    plt.figure(figsize=(10, 5))
    for country, grp in df.groupby("country"):
        grp = grp.sort_values("date")
        plt.plot(grp["date"], grp["cumulative_cases"], label=country)
    plt.title("Cumulative Cases Over Time")
    plt.xlabel("Date")
    plt.ylabel("Cumulative Cases")
    plt.legend(fontsize=8)
    plt.tight_layout()
    plt.savefig("chart_cumulative_cases.png", dpi=150)
    plt.close()

    # Chart 2: total new cases by country (bar)
    totals = df.groupby("country")["new_cases"].sum().sort_values(ascending=False)
    plt.figure(figsize=(8, 4))
    totals.plot(kind="bar", color="#C0392B")
    plt.title("Total New Cases by Country (period total)")
    plt.ylabel("New Cases")
    plt.tight_layout()
    plt.savefig("chart_total_cases_by_country.png", dpi=150)
    plt.close()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--offline", action="store_true", help="skip the live API call")
    args = parser.parse_args()

    df = get_data(force_offline=args.offline)
    df.to_csv("processed_covid_data.csv", index=False)

    print("\n=== Latest cumulative cases by country ===")
    latest = df.sort_values("date").groupby("country").tail(1)
    print(latest[["country", "date", "cumulative_cases"]].to_string(index=False))

    make_charts(df)
    print("\nCharts saved: chart_cumulative_cases.png, chart_total_cases_by_country.png")


if __name__ == "__main__":
    main()
