"""
api_fetch.py
Fetch daily mandi (Agmarknet) data from data.gov.in API.
"""

import os
import requests
import json
from datetime import datetime

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")
os.makedirs(DATA_DIR, exist_ok=True)


API_URL = "https://api.data.gov.in/resource/9ef84268-d588-465a-a308-a864a43d0070"
API_KEY = "--"  # Replace this with your API key

API_URL = "https://api.data.gov.in/resource/9ef84268-d588-465a-a308-a864a43d0070" #current daily price of various commodities from various markets(mandi)
API_KEY = "579b464db66ec23bdd0000018abf3ffd640741a37a72560a94ff1071"  # Replace this with your API key


def fetch_agmarknet_data(limit=5000, max_records=10000):
    """Fetch mandi data in batches and save as JSON."""
    all_records = []
    offset = 0

    print(f"Fetching Agmarknet data (limit={limit})...")

    while offset < max_records:
        params = {
            "api-key": API_KEY,
            "format": "json",
            "limit": limit,
            "offset": offset
        }

        res = requests.get(API_URL, params=params)
        if res.status_code != 200:
            print(f"[ERROR] API call failed: {res.status_code}")
            break

        data = res.json().get("records", [])
        if not data:
            break

        all_records.extend(data)
        offset += limit
        print(f"[INFO] Fetched {len(data)} records (offset={offset})")

    # Save to JSON file
    out_path = os.path.join(DATA_DIR, "mandi_data.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(all_records, f, indent=2)

    print(f"[OK] Saved {len(all_records)} mandi records -> {out_path}")

if __name__ == "__main__":
    fetch_agmarknet_data()
