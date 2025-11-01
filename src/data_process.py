"""
data_process.py
Enhanced cleaning and aggregation for Agmarknet mandi data.
"""

import os
import json
import pandas as pd

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")

def clean_mandi_data():
    input_path = os.path.join(DATA_DIR, "mandi_data.json")
    output_path = os.path.join(DATA_DIR, "mandi_clean.csv")

    if not os.path.exists(input_path):
        print("[ERROR] Input JSON not found.")
        return

    with open(input_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    df = pd.DataFrame(data)

    required_cols = [
        "state", "district", "market", "commodity",
        "variety", "arrival_date", "min_price", "max_price",
        "modal_price"
    ]

    df = df[[c for c in required_cols if c in df.columns]]

    # ✅ Convert data types
    df["arrival_date"] = pd.to_datetime(df["arrival_date"], errors="coerce")
    df["min_price"] = pd.to_numeric(df["min_price"], errors="coerce")
    df["max_price"] = pd.to_numeric(df["max_price"], errors="coerce")
    df["modal_price"] = pd.to_numeric(df["modal_price"], errors="coerce")

    # ✅ Drop invalid rows
    df.dropna(subset=["state", "commodity", "arrival_date"], inplace=True)

    # ✅ Aggregate monthly average — but keep `market`
    monthly_avg = (
        df.groupby([
            df["state"], df["district"], df["market"],
            df["commodity"], df["arrival_date"].dt.to_period("M")
        ])
        .agg({"modal_price": "mean"})
        .reset_index()
    )

    monthly_avg.rename(columns={"arrival_date": "date"}, inplace=True)
    monthly_avg["date"] = monthly_avg["date"].astype(str)

    monthly_avg.to_csv(output_path, index=False)
    print(f"[OK] Cleaned and saved data -> {output_path}")


if __name__ == "__main__":
    clean_mandi_data()
