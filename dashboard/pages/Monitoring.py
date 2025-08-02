import streamlit as st
import pandas as pd
import os
import json
from utils.override_handler import load_scheduled_overrides
from utils.rules_override_handler import load_rule_scheduled_overrides

st.set_page_config(page_title="Monitoring", layout="wide")
st.title("📊 AI Monitoring Dashboard")

# Load data
DATA_PATH = "data/mock_product_data.xlsx"
RECOMMENDATION_LOG = "data/scheduled_changes.json"

# --- Load Product Data
if os.path.exists(DATA_PATH):
    df = pd.read_excel(DATA_PATH)
else:
    st.error("❌ Product data file not found.")
    st.stop()

# --- Load Scheduled AI Changes
scheduled_changes = []
if os.path.exists(RECOMMENDATION_LOG):
    try:
        with open(RECOMMENDATION_LOG, "r") as f:
            scheduled_changes = json.load(f)
    except json.JSONDecodeError:
        scheduled_changes = []

# --- Section: Recent AI Price Changes
st.subheader("📈 Recently Scheduled AI Price Changes")
manual = load_scheduled_overrides()
rule_based = load_rule_scheduled_overrides()

# Combine both with a label
for m in manual:
    m["type"] = "Manual"
for r in rule_based:
    r["type"] = "Rule"

combined = manual + rule_based

if combined:
    df_combined = pd.DataFrame(combined)
    display_cols = ["product", "new_price", "reason", "scheduled_for", "expires_on", "type"]
    df_combined = df_combined[display_cols] if all(col in df_combined.columns for col in display_cols) else df_combined
    df_combined = df_combined.sort_values("scheduled_for", ascending=False)
    st.dataframe(df_combined, use_container_width=True)
else:
    st.info("No recent price changes scheduled.")

# --- Section: Outlier Pricing Detection
st.subheader("🚨 Price Outlier Detection")

# Add derived competitor average
df["Competitor Price"] = df[["Amazon Price", "Flipkart Price", "Croma Price"]].mean(axis=1)

outliers = df[df["Our Price"] > df["Competitor Price"] * 1.5]
if not outliers.empty:
    st.error("Some prices are unusually high compared to competitors!")
    st.dataframe(outliers)
else:
    st.success("✅ No major price outliers found.")

# --- Section: AI Confidence Score Check
if "Confidence Score" in df.columns:
    st.subheader("🧠 AI Confidence Monitoring")

    low_conf = df[df["Confidence Score"] < 0.7]
    if not low_conf.empty:
        st.warning("⚠️ Low-confidence predictions need review:")
        st.dataframe(low_conf)
    else:
        st.success("✅ All AI price predictions have acceptable confidence.")

# --- Section: Summary Stats
st.subheader("📊 Dashboard Metrics")

col1, col2, col3 = st.columns(3)

col1.metric("Total Products", len(df))
col2.metric("Outlier Prices", len(outliers))
col3.metric("Low Confidence", len(df[df.get("Confidence Score", 1) < 0.7]))

# --- Optional: Visual Insights (if needed)
st.markdown("---")
st.subheader("📉 Price vs Competitor Price Chart")

try:
    st.line_chart(df[["Our Price", "Competitor Price"]])
except:
    st.info("Price chart requires numeric data to plot.")
