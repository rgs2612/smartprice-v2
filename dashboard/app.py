import streamlit as st
import pandas as pd
import sys
import os

# Dynamically add project root to Python path
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from utils.data_loader import load_product_data

st.set_page_config(page_title="Smart Price AI Dashboard", layout="wide")

st.title("🧠 Smart Price AI Dashboard")

st.markdown("""
Welcome to the AI-powered pricing control center. Use the sidebar to navigate:
- 📈 View Recommendations
- 🛠️ Override Pricing
- 📋 Set Pricing Rules
- 📡 Monitoring
- 🔔 Notifications
""")

from utils.override_handler import apply_overrides

# Load data preview
df = load_product_data()
df = apply_overrides(df)

st.subheader("📊 Price Overview")
st.dataframe(df, use_container_width=True)

from ai.demand_forecaster import train_demand_model
from utils.data_loader import load_product_data

# Sidebar trigger
with st.sidebar:
    st.markdown("## 🧠 AI Training Options")
    if st.button("📈 Train Demand Forecast Model"):
        df = load_product_data()
        train_demand_model(df)
        st.success("✅ Demand model trained and saved!")
