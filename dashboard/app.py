# pages/Price_Overview.py
import streamlit as st
import pandas as pd
import os
import json
import sys
from datetime import datetime

# Set Python path to root
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from utils.data_loader import load_product_data

# File paths
MANUAL_OVERRIDE_FILE = "data/scheduled_changes.json"
RULE_OVERRIDE_FILE = "data/rule_scheduled_changes.json"
AI_OVERRIDE_FILE = "data/ai_scheduled.json"

st.set_page_config(page_title="Price Overview", layout="wide")
st.title("\U0001F4CA Product Price Overview")

with st.sidebar:
    st.title("🧠 Smart Price AI")
    st.markdown("AI-powered pricing assistant")

# Add Refresh Button
if st.button("\U0001F504 Refresh Data"):
    st.rerun()

# Load product data
df = load_product_data()

# Base column defaults
if "Price" not in df.columns:
    df["Price"] = df["Our Price"]
if "OverrideType" not in df.columns:
    df["OverrideType"] = None


# --- COMBINED OVERRIDE FUNCTION ---
def apply_all_overrides(df):
    df = df.copy()
    now = datetime.now()

    # Load overrides
    def safe_load(file):
        try:
            with open(file, "r") as f:
                return json.load(f)
        except:
            return []

    manual = safe_load(MANUAL_OVERRIDE_FILE)
    rules = safe_load(RULE_OVERRIDE_FILE)
    ai = safe_load(AI_OVERRIDE_FILE)

    applied = {"Manual": 0, "Rule-Based": 0, "AI Recommended": 0}

    # Step 1: Manual Overrides
    for ovr in manual:
        try:
            pid = ovr["product_id"]
            new_price = ovr["new_price"]
            start = datetime.strptime(ovr["scheduled_for"], "%Y-%m-%d %H:%M:%S")
            end = datetime.strptime(ovr["expires_on"], "%Y-%m-%d %H:%M:%S")

            if start <= now <= end:
                mask = df["ProductID"] == pid
                df.loc[mask, "Price"] = new_price
                df.loc[mask, "Our Price"] = round(new_price)
                df.loc[mask, "OverrideType"] = "Manual"
                applied["Manual"] += df.loc[mask].shape[0]
        except Exception as e:
            print(f"[Manual Override Error] {e}")

    # Step 2: Rule-Based Overrides
    for ovr in rules:
        try:
            pid = ovr["product_id"]
            new_price = ovr["new_price"]
            start = datetime.strptime(ovr["scheduled_for"], "%Y-%m-%d %H:%M:%S")
            end = datetime.strptime(ovr["expires_on"], "%Y-%m-%d %H:%M:%S")

            if start <= now <= end:
                mask = (df["ProductID"] == pid) & (
                    df["OverrideType"].isna() | (df["OverrideType"] == "None")
                )
                df.loc[mask, "Price"] = new_price
                df.loc[mask, "Our Price"] = round(new_price)
                df.loc[mask, "OverrideType"] = "Rule-Based"
                applied["Rule-Based"] += df.loc[mask].shape[0]
        except Exception as e:
            print(f"[Rule Override Error] {e}")

    # Step 3: AI Recommendations (auto-applied)
    for ovr in ai:
        try:
            pid = ovr["product_id"]
            new_price = ovr["ai_price"]
            confidence = ovr.get("confidence", None)

            mask = (df["ProductID"] == pid) & (
                df["OverrideType"].isna() | (df["OverrideType"] == "None")
            )
            df.loc[mask, "Price"] = round(new_price)
            df.loc[mask, "Our Price"] = round(new_price)
            df.loc[mask, "Confidence Score"] = confidence
            df.loc[mask, "OverrideType"] = "AI Recommended"
            applied["AI Recommended"] += df.loc[mask].shape[0]
        except Exception as e:
            print(f"[AI Recommendation Error] {e}")

    st.success(f"\u2705 Overrides Applied: {applied}")
    return df

# --- Apply Overrides ---
df = apply_all_overrides(df)

# --- Highlight Rows by Override ---
def highlight_overrides(row):
    override = row.get("OverrideType")
    if override == "Manual":
        return ["background-color: #fff3e0"] * len(row)
    elif override == "Rule-Based":
        return ["background-color: #e0f7fa"] * len(row)
    elif override == "AI Recommended":
        return ["background-color: #e6ffe6"] * len(row)
    return [""] * len(row)

# --- Legend ---
st.markdown(
    """
    <b>\u2728 Legend:</b><br>
    <span style="background-color:#fff3e0;">&nbsp;&nbsp;&nbsp;</span> Manual Override &nbsp;&nbsp;
    <span style="background-color:#e0f7fa;">&nbsp;&nbsp;&nbsp;</span> Rule-Based Override &nbsp;&nbsp;
    <span style="background-color:#e6ffe6;">&nbsp;&nbsp;&nbsp;</span> AI Recommended
    """,
    unsafe_allow_html=True,
)

# --- Display Table ---
columns_to_show = [
    "ProductID", "ProductName", "TrendScore", "Stock Level", "Demand", "Forecast Demand",
    "Confidence Score", "Amazon Price", "Flipkart Price", "Croma Price", "Our Price", "OverrideType"
]

format_dict = {
    "TrendScore": "{:.2f}",
    "Stock Level": "{:,.0f}",
    "Demand": "{:.2f}",
    "Forecast Demand": "{:.2f}",
    "Confidence Score": "{:.2f}",
    "Amazon Price": "{:,.0f}",
    "Flipkart Price": "{:,.0f}",
    "Croma Price": "{:,.0f}",
    "Our Price": "{:,.0f}"
}

st.subheader("\U0001F4B9 Final Product Prices with Overrides Applied")
styled_df = df[columns_to_show].style.apply(highlight_overrides, axis=1).format(format_dict)
st.dataframe(styled_df, use_container_width=True)
