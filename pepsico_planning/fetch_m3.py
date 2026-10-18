"""Download Census M3 (Manufacturers' Shipments, Inventories and Orders) from the official Census API.

Source: https://api.census.gov/data/timeseries/eits/m3
Run:    python pepsico_planning/fetch_m3.py
Output: data/raw/m3_raw.csv  (every category and data type, one row per month)

The Census API needs a free key (https://api.census.gov/data/key_signup.html).
The script reads it from the CENSUS_API_KEY environment variable, or asks you to paste it.
The key is never written to a file.
"""
import os
import re
import time
from datetime import date
from pathlib import Path

import pandas as pd
import requests

API_URL = "https://api.census.gov/data/timeseries/eits/m3"
FIELDS = "data_type_code,time_slot_id,seasonally_adj,category_code,cell_value,error_data"
START_YEAR = 2015
RAW_PATH = Path(__file__).resolve().parents[1] / "data" / "raw" / "m3_raw.csv"


def get_key() -> str:
    key = os.environ.get("CENSUS_API_KEY", "").strip()
    if not key:
        key = input("Paste your Census API key and press Enter: ").strip()
    if not re.fullmatch(r"[0-9a-fA-F]{40}", key):
        print(f"WARNING: the key you gave is {len(key)} characters and does not look like a Census key "
              "(expected 40 letters/numbers). Copy it again from the Census email.")
    return key


def plain_text(body: str, limit: int = 300) -> str:
    """Strip HTML tags so a server error page is readable."""
    text = re.sub(r"<script.*?</script>|<style.*?</style>", " ", body, flags=re.S | re.I)
    text = re.sub(r"<[^>]+>", " ", text)
    return re.sub(r"\s+", " ", text).strip()[:limit]


def fetch_year(year: int, key=None) -> pd.DataFrame:
    """One API call per year (the same call shape the Census documents)."""
    params = {"get": FIELDS, "for": "us:*", "time": str(year)}
    if key:
        params["key"] = key
    last_problem = ""
    for attempt in range(3):
        resp = requests.get(API_URL, params=params, timeout=60)
        if resp.status_code == 204 or (resp.status_code == 200 and not resp.text.strip()):
            return pd.DataFrame()
        if resp.status_code == 200:
            try:
                rows = resp.json()
            except ValueError:
                last_problem = (f"HTTP 200 but the reply was not data. Content-Type: "
                                f"{resp.headers.get('content-type')}. Server said: {plain_text(resp.text)!r}")
                break  # retrying will not change a rejected key
            return pd.DataFrame(rows[1:], columns=rows[0])
        last_problem = f"HTTP {resp.status_code}: {plain_text(resp.text)!r}"
        time.sleep(2 * (attempt + 1))
    raise SystemExit(
        f"\nCensus API did not return data for {year}.\n  {last_problem}\n"
        "If this mentions the key, check it is the 40-character key from the Census email "
        "and that you clicked the activation link."
    )


def main() -> None:
    key = get_key()
    frames = []
    for year in range(START_YEAR, date.today().year + 1):
        df = fetch_year(year, key)
        print(f"{year}: {len(df)} rows")
        if len(df):
            frames.append(df)
    if not frames:
        raise SystemExit("No data downloaded.")
    data = pd.concat(frames, ignore_index=True)
    data["value"] = pd.to_numeric(data["cell_value"], errors="coerce")
    data["month"] = pd.to_datetime(data["time"] + "-01", errors="coerce")
    RAW_PATH.parent.mkdir(parents=True, exist_ok=True)
    data.to_csv(RAW_PATH, index=False)
    print(f"\nSaved {len(data)} rows to {RAW_PATH}")
    print(f"Months covered: {data['month'].min():%Y-%m} to {data['month'].max():%Y-%m}")


if __name__ == "__main__":
    main()
