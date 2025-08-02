# pages/Notifications.py
import streamlit as st
import pandas as pd
import os
from utils.action_generator import generate_action

st.set_page_config(page_title="Notifications", page_icon="🔔")
st.title("📣 Smart Pricing Notifications")
st.markdown("Real-time alerts generated from AI monitoring logic.")

# Load data
data_path = "data/mock_product_data.xlsx"
if not os.path.exists(data_path):
    st.warning("Product data not found.")
    st.stop()

df = pd.read_excel(data_path)

# Safe checks for missing columns
required_cols = ["ProductName", "Stock Level", "Confidence Score", "Competitor Price", "Our Price"]
for col in required_cols:
    if col not in df.columns:
        st.error(f"Missing required column: **{col}**")
        st.stop()

# Apply action logic
df = generate_action(df)

# Notification Sections
st.subheader("🔻 Low Stock Alerts (< 5 units)")
low_stock = df[df["Stock Level"] < 5]
if not low_stock.empty:
    st.error("The following products are critically low on stock:")
    st.dataframe(low_stock[["ProductName", "Stock Level", "Action"]])
else:
    st.success("✅ All products have sufficient stock.")

st.subheader("⚠️ Price Gap Alerts (> ₹2000 difference)")
price_gap = df[df["Price Gap"] > 2000]
if not price_gap.empty:
    st.warning("These products have a large price difference with competitors:")
    st.dataframe(price_gap[["ProductName", "Competitor Price", "Our Price", "Price Gap", "Action"]])
else:
    st.success("✅ No large price mismatches detected.")

st.subheader("🤖 Low AI Confidence (< 70%)")
low_confidence = df[df["Confidence Score"] < 0.70]
if not low_confidence.empty:
    st.info("These products have low model confidence. Manual review recommended:")
    st.dataframe(low_confidence[["ProductName", "Confidence Score", "Action"]])
else:
    st.success("✅ All predictions have high confidence.")

# Summary Badge
st.markdown("---")
st.markdown("✅ **Smart alerts help you stay ahead of risks and pricing mismatches.**")

