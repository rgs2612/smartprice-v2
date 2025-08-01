import streamlit as st
import pandas as pd
import json
import os
from datetime import datetime, timedelta

SCHEDULE_FILE = "data/scheduled_changes.json"

# Load mock product data
@st.cache_data
def load_data():
    return pd.read_excel("data/mock_product_data.xlsx")

def save_schedule(schedule):
    os.makedirs("data", exist_ok=True)
    if os.path.exists(SCHEDULE_FILE):
        with open(SCHEDULE_FILE, "r") as f:
            all_schedules = json.load(f)
    else:
        all_schedules = []

    all_schedules.append(schedule)
    with open(SCHEDULE_FILE, "w") as f:
        json.dump(all_schedules, f, indent=2)

# UI
st.title("📅 Price Scheduling")

df = load_data()
product_names = df['ProductName'].tolist()
selected_product = st.selectbox("Select a Product", product_names)

new_price = st.number_input("Enter New Price", min_value=1.0, step=1.0)

# Select date and time separately
schedule_date = st.date_input(
    "Select Date",
    min_value=datetime.today().date(),
    value=datetime.today().date()
)

schedule_time = st.time_input(
    "Select Time",
    value=(datetime.now() + timedelta(hours=1)).time()
)

# Combine to datetime
schedule_datetime = datetime.combine(schedule_date, schedule_time)

# Validate and save
if schedule_datetime < datetime.now():
    st.warning("⏰ Please select a future date and time.")
else:
    if st.button("📆 Schedule Price Change", key="schedule_btn"):
        schedule = {
            "product": selected_product,
            "new_price": new_price,
            "scheduled_for": schedule_datetime.strftime("%Y-%m-%d %H:%M:%S")
        }
        save_schedule(schedule)
        st.success(f"✅ Scheduled price change for {selected_product} at {schedule_datetime}.")

# Display existing scheduled changes
if os.path.exists(SCHEDULE_FILE):
    with open(SCHEDULE_FILE, "r") as f:
        existing = json.load(f)
    if existing:
        st.subheader("🕒 Scheduled Changes")
        st.table(pd.DataFrame(existing))
    else:
        st.info("No scheduled changes yet.")
else:
    st.info("No schedule file found.")
