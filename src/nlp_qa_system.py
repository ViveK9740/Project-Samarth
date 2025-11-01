# -*- coding: utf-8 -*-
"""
nlp_qa_system.py
Project Samarth – Fully NLP-Enabled Agricultural Q&A System
"""

import os
import re
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
import spacy

# Load NLP model
nlp = spacy.load("en_core_web_sm")

# ---------------------------------------------------------
# Load and prepare data
# ---------------------------------------------------------
def load_data():
    base_dir = os.path.dirname(os.path.dirname(__file__))
    data_path = os.path.join(base_dir, "data", "mandi_clean.csv")

    if not os.path.exists(data_path):
        print("[WARN] mandi_clean.csv not found.")
        return pd.DataFrame()

    df = pd.read_csv(data_path)
    df.columns = [c.strip().lower().replace(" ", "_") for c in df.columns]

    if "date" in df.columns:
        df["date"] = pd.to_datetime(df["date"], errors="coerce")

    return df


# ---------------------------------------------------------
# Core NLP Q&A Class
# ---------------------------------------------------------
class AgriQA:
    def __init__(self):
        self.df = load_data()
        if self.df.empty:
            print("[WARN] Empty dataframe loaded.")

    # -----------------------------------------------------
    # NLP Entity Extraction
    # -----------------------------------------------------
    def extract_entities(self, question):
        """Extract commodity, market/state, and intent."""
        doc = nlp(question.lower())

        commodity = None
        location = None
        intent = "price"

        # Named entity extraction
        for ent in doc.ents:
            if ent.label_ in ["GPE", "LOC"]:
                location = ent.text.strip()
            elif ent.label_ in ["PRODUCT", "ORG", "NORP"]:
                commodity = ent.text.strip()

        # Heuristic fallback (regex)
        if not commodity:
            m = re.search(r"(tomato|onion|potato|brinjal|rice|paddy|wheat|maize|banana|apple)", question.lower())
            if m:
                commodity = m.group(1)
        if not location:
            m = re.search(r"in\s+([a-zA-Z ]+)", question.lower())
            if m:
                location = m.group(1).strip()

        # Intent detection
        if re.search(r"trend|increase|decrease|last|past|month|week|year", question):
            intent = "trend"
        elif re.search(r"highest|max|top", question):
            intent = "highest"
        elif re.search(r"lowest|min|cheap", question):
            intent = "lowest"
        elif re.search(r"average|mean", question):
            intent = "average"
        elif re.search(r"price|rate|value|cost", question):
            intent = "price"

        return commodity, location, intent

    # -----------------------------------------------------
    # Query Handlers
    # -----------------------------------------------------
    def handle_price_query(self, commodity, location):
        df = self.df.copy()

        if commodity:
            df = df[df["commodity"].str.contains(commodity, case=False, na=False)]
        if location:
            df = df[df["market"].str.contains(location, case=False, na=False) |
                    df["state"].str.contains(location, case=False, na=False)]

        if df.empty:
            return f"No recent data found for {commodity or 'commodity'} in {location or 'any location'}."

        latest_date = df["date"].max()
        latest_data = df[df["date"] == latest_date]
        avg_price = latest_data["modal_price"].mean()

        return f"🟢 The latest **average modal price** of **{commodity.title() if commodity else 'commodity'}** in **{location.title() if location else 'India'}** is **₹{avg_price:.2f}** (as of {latest_date.date()})."

    def handle_trend_query(self, commodity, location):
        df = self.df.copy()
        if commodity:
            df = df[df["commodity"].str.contains(commodity, case=False, na=False)]
        if location:
            df = df[df["market"].str.contains(location, case=False, na=False) |
                    df["state"].str.contains(location, case=False, na=False)]

        if df.empty or "date" not in df.columns:
            return f"No trend data found for {commodity or 'commodity'} in {location or 'any location'}."

        recent = df.sort_values("date").tail(12)
        trend_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "trend.png")

        plt.figure(figsize=(6, 3))
        plt.plot(recent["date"], recent["modal_price"], marker="o", color="#27ae60")
        plt.title(f"{commodity.title() if commodity else 'Commodity'} Price Trend in {location.title() if location else 'India'}")
        plt.xlabel("Date")
        plt.ylabel("Price (₹/quintal)")
        plt.tight_layout()
        plt.savefig(trend_path)
        plt.close()

        return f"📈 Price trend for **{commodity.title() if commodity else 'commodity'}** in **{location.title() if location else 'India'}** generated."

    def handle_high_low_query(self, commodity, intent="highest"):
        df = self.df.copy()
        if commodity:
            df = df[df["commodity"].str.contains(commodity, case=False, na=False)]

        if df.empty:
            return f"No data found for {commodity or 'commodity'}."

        grouped = df.groupby("market")["modal_price"].mean().reset_index()
        best_row = grouped.loc[grouped["modal_price"].idxmax()] if intent == "highest" else grouped.loc[grouped["modal_price"].idxmin()]

        arrow = "⬆️" if intent == "highest" else "⬇️"
        return f"{arrow} The **{intent} average modal price** for **{commodity.title()}** is in **{best_row['market']}**, with **₹{best_row['modal_price']:.2f}."

    # -----------------------------------------------------
    # Main answer handler
    # -----------------------------------------------------
    def answer_question(self, question: str):
        commodity, location, intent = self.extract_entities(question)

        if intent == "trend":
            return self.handle_trend_query(commodity, location)
        elif intent == "highest":
            return self.handle_high_low_query(commodity, "highest")
        elif intent == "lowest":
            return self.handle_high_low_query(commodity, "lowest")
        elif intent in ["price", "average"]:
            return self.handle_price_query(commodity, location)
        else:
            return "Sorry, I couldn’t understand your question clearly. Please rephrase it."


# ---------------------------------------------------------
# Factory Function
# ---------------------------------------------------------
def get_answer():
    return AgriQA()
