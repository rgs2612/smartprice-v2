import streamlit as st
import pandas as pd
from sklearn.linear_model import LinearRegression
import joblib

st.title("🧠 AI Training Options")

st.subheader("📈 Train Demand Forecast Model")

if st.button("Train Demand Forecast Model"):
    try:
        df = pd.read_excel("data/mock_product_data.xlsx")
        required = ["TrendScore", "Stock Level", "Competitor Price", "Demand"]

        if not all(col in df.columns for col in required):
            st.error(f"Missing columns: {set(required) - set(df.columns)}")
        else:
            X = df[["TrendScore", "Stock Level", "Competitor Price"]]
            y = df["Demand"]

            model = LinearRegression()
            model.fit(X, y)

            joblib.dump(model, "ai/demand_forecast_model.pkl")
            st.success("✅ Demand Forecast Model trained and saved.")
    except Exception as e:
        st.error(f"❌ Error: {e}")
