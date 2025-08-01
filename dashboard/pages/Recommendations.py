# dashboard/pages/Recommendations.py

import streamlit as st
import pandas as pd
from utils.data_loader import load_product_data
from ai.predictor import predict_optimal_price

st.title("🤖 AI-Powered Price Recommendations")

# Load product data
df = load_product_data()

# Apply AI price prediction
df["AI Price"] = df.apply(predict_optimal_price, axis=1)

# Toggle to apply AI price
st.markdown("#### 🔧 Pricing Mode")
use_ai = st.toggle("Use AI-Suggested Price", value=True)

df["Final Price"] = df["AI Price"] if use_ai else df["Our Price"]

# Show price suggestions
st.markdown("### 📈 Price Suggestions Table")
st.dataframe(df[[
    "ProductName", "TrendScore", "Demand", "Stock Level",
    "Amazon Price", "Flipkart Price", "Croma Price",
    "Our Price", "AI Price", "Final Price"
]])
