# pages/Notifications.py
import streamlit as st
import pandas as pd
import os
import json
from utils.action_generator import generate_action

st.set_page_config(page_title="Notifications", page_icon="🔔")
st.title("📣 Smart Pricing Notifications")
st.markdown("Real-time alerts generated from AI monitoring logic.")

# File paths
DATA_PATH = "data/mock_product_data.xlsx"
MANUAL_OVERRIDE_PATH = "data/scheduled_changes.json"
RULE_OVERRIDE_PATH = "data/rule_scheduled_changes.json"
AI_OVERRIDE_PATH = "data/ai_scheduled.json"

# Load product data
if not os.path.exists(DATA_PATH):
    st.warning("Product data not found.")
    st.stop()

df = pd.read_excel(DATA_PATH)

# Price gap
df["Price Gap"] = abs(df["Our Price"] - df["Competitor Price"])

# Required columns
required_cols = ["ProductID", "ProductName", "Stock Level", "Confidence Score", "Competitor Price", "Our Price"]
for col in required_cols:
    if col not in df.columns:
        st.error(f"Missing required column: **{col}**")
        st.stop()

# Load overrides safely
def load_json(path):
    if os.path.exists(path):
        with open(path, "r") as f:
            try:
                return json.load(f)
            except:
                return []
    return []

manual_overrides = load_json(MANUAL_OVERRIDE_PATH)
rule_overrides = load_json(RULE_OVERRIDE_PATH)
ai_overrides = load_json(AI_OVERRIDE_PATH)

# Prepare a mapping: ProductID -> Action Taken
action_taken_map = {}

for o in manual_overrides:
    pid = o.get("product_id")
    if pid: action_taken_map[pid] = "Manual Override"

for o in rule_overrides:
    pid = o.get("product_id")
    if pid: action_taken_map[pid] = "Rule-Based Override"

for o in ai_overrides:
    pid = o.get("product_id")
    if pid: action_taken_map[pid] = "AI Recommended"

# Add column to df
df["Action Taken"] = df["ProductID"].apply(lambda pid: action_taken_map.get(pid, "None"))

# Apply AI logic-based action recommendations
df = generate_action(df)

# --- Sections ---
st.subheader("🔻 Low Stock Alerts (< 5 units)")
low_stock = df[df["Stock Level"] < 5]
if not low_stock.empty:
    st.error("The following products are critically low on stock:")
    st.dataframe(low_stock[["ProductID", "ProductName", "Stock Level", "Action", "Action Taken"]])
else:
    st.success("✅ All products have sufficient stock.")

st.subheader("⚠️ Price Gap Alerts (> ₹2000 difference)")
price_gap = df[df["Price Gap"] > 2000]
if not price_gap.empty:
    st.warning("These products have a large price difference with competitors:")
    st.dataframe(price_gap[["ProductID", "ProductName", "Competitor Price", "Our Price", "Price Gap", "Action", "Action Taken"]])
else:
    st.success("✅ No large price mismatches detected.")

st.subheader("🤖 Low AI Confidence (< 70%)")
low_confidence = df[df["Confidence Score"] < 0.70]
if not low_confidence.empty:
    st.info("These products have low model confidence. Manual review recommended:")
    st.dataframe(low_confidence[["ProductID", "ProductName", "Confidence Score", "Action", "Action Taken"]])
else:
    st.success("✅ All predictions have high confidence.")

st.markdown("---")
st.markdown("✅ **Smart alerts help you stay ahead of risks and pricing mismatches.**")
