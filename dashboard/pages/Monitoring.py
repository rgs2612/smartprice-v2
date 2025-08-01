import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np
from utils.data_loader import load_product_data

st.title("📡 Monitoring & Alerts")

df = load_product_data()

st.markdown("### 🗺️ Regional Price Variations (Simulated)")

# Simulated price data by region
regions = ["Delhi", "Mumbai", "Bangalore", "Chennai", "Hyderabad"]
region_prices = np.random.randint(40000, 80000, size=len(regions))

region_df = pd.DataFrame({
    "Region": regions,
    "Avg Price": region_prices
})

bar_chart = px.bar(region_df, x="Region", y="Avg Price", color="Avg Price",
                   title="Regional Price Differences", text="Avg Price")

st.plotly_chart(bar_chart, use_container_width=True)

# -------------------------------
st.markdown("### 📈 Price Change Timeline (Simulated)")

product = st.selectbox("Select product", df["ProductName"])
days = pd.date_range(end=pd.Timestamp.today(), periods=10)

# Generate fake price trend
price_trend = pd.DataFrame({
    "Date": days,
    "Price": np.random.normal(loc=df[df["ProductName"] == product]["Our Price"].values[0], scale=500, size=10).astype(int)
})

line_chart = px.line(price_trend, x="Date", y="Price", title=f"{product} – 10-Day Price Trend")
st.plotly_chart(line_chart, use_container_width=True)

# -------------------------------
st.markdown("### 🚨 Exception Alerts")

alerts = [
    "⚠️ Flipkart undercut your price on OnePlus 12 by ₹1,500",
    "⚠️ iPhone 14 sales dropped 20% this week",
    "✅ Your pricing rule saved ₹5,000 on Samsung Galaxy S23"
]

for alert in alerts:
    st.write(alert)
