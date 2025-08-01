import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import random

st.title("🔔 Notification Center")

# --- Simulated notifications data ---
types = ["Competitor Price Change", "Demand Spike", "Rule Triggered"]
messages = [
    "Amazon dropped price for Galaxy S23 by ₹2,000",
    "High demand detected for iPhone 14 in Bangalore",
    "Rule #2 triggered: Inventory < 10% on OnePlus 12",
    "Flipkart matched your price on Pixel 8",
    "Rule #3: Aggressive pricing applied for OnePlus Nord",
    "Demand spike alert for Samsung A55"
]

def generate_fake_notifications(n=10):
    return pd.DataFrame({
        "Time": [datetime.now() - timedelta(minutes=15 * i) for i in range(n)],
        "Type": [random.choice(types) for _ in range(n)],
        "Message": random.choices(messages, k=n)
    })

df = generate_fake_notifications(10)

# --- Filters ---
st.markdown("### 📍 Filter Notifications")
selected_type = st.selectbox("Filter by Type", ["All"] + types)

if selected_type != "All":
    df = df[df["Type"] == selected_type]

# --- Display Notifications ---
st.markdown("### 📬 Recent Alerts")
for _, row in df.iterrows():
    with st.container():
        st.markdown(f"🕒 {row['Time'].strftime('%Y-%m-%d %H:%M:%S')}")
        st.markdown(f"**📌 {row['Type']}** — {row['Message']}")
        st.markdown("---")

# --- Export ---
st.download_button("📤 Export Notifications", data=df.to_csv(index=False), file_name="notifications.csv")
