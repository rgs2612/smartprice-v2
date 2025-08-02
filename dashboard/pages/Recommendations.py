import streamlit as st
import pandas as pd
import joblib
from datetime import datetime

# File paths
DATA_PATH = "data/mock_product_data.xlsx"
MODEL_PATH = "ai/ai_price_model.pkl"

st.title("🧠 AI Pricing Recommendations")

# Load product data
try:
    df = pd.read_excel(DATA_PATH)
except FileNotFoundError:
    st.error("❌ Product data file not found.")
    st.stop()

# Load AI model
try:
    model = joblib.load(MODEL_PATH)
except FileNotFoundError:
    st.error("❌ AI model not trained yet. Please train it first.")
    st.stop()

# Validate required columns
required_cols = ["TrendScore", "Stock Level", "Demand", "Competitor Price"]
missing = [col for col in required_cols if col not in df.columns]
if missing:
    st.error(f"Missing required columns: {missing}")
    st.stop()

# Predict AI prices
features = df[required_cols]
df["AI Price"] = model.predict(features)

# Confidence Score
df["Confidence Score"] = 100 - abs(df["AI Price"] - df["Competitor Price"]) / df["Competitor Price"] * 100
df["Confidence Score"] = df["Confidence Score"].round(2)

# Ensure required metadata columns
if "Reason" not in df.columns:
    df["Reason"] = None
if "override_applied" not in df.columns:
    df["override_applied"] = False
if "Original Price" not in df.columns:
    df["Original Price"] = df["Our Price"]  # Store original at first run

# --- Show AI Suggestions ---
st.markdown("### 🧠 Suggested Prices (AI Only)")
st.dataframe(df[["ProductName", "Competitor Price", "AI Price", "Confidence Score", "Our Price", "Reason", "override_applied"]], use_container_width=True)

# --- Manual Review & Actions ---
st.markdown("### ✋ Manual Review & Actions")

flagged = df[df["Confidence Score"] < 85]

if not flagged.empty:
    for i, row in flagged.iterrows():
        with st.expander(f"🔍 {row['ProductName']} - {row['Confidence Score']}% confidence"):
            st.write(f"- **Competitor Price:** ₹{row['Competitor Price']}")
            st.write(f"- **AI Suggested Price:** ₹{row['AI Price']:.2f}")
            st.write(f"- **Current Our Price:** ₹{row['Our Price']}")
            st.write(f"- **Original Price:** ₹{row['Original Price'] if 'Original Price' in row else 'N/A'}")

            col1, col2 = st.columns(2)

            with col1:
                if not row["override_applied"]:
                    if st.button(f"✅ Apply AI Price - {row['ProductName']}", key=f"apply_{i}"):
                        df.at[i, "Original Price"] = row["Our Price"]
                        df.at[i, "Our Price"] = row["AI Price"]
                        df.at[i, "Reason"] = "Manual AI Override"
                        df.at[i, "override_applied"] = True
                        try:
                            df.to_excel(DATA_PATH, index=False)
                            st.success(f"✅ Applied AI Price ₹{row['AI Price']:.2f} to {row['ProductName']}")
                            st.rerun()
                        except PermissionError:
                            st.warning("⚠️ Excel file is open. Please close and try again.")
            with col2:
                if row["override_applied"]:
                    if st.button(f"↩️ Revert Price - {row['ProductName']}", key=f"revert_{i}"):
                        df.at[i, "Our Price"] = row["Original Price"]
                        df.at[i, "Reason"] = "Reverted AI Override"
                        df.at[i, "override_applied"] = False
                        try:
                            df.to_excel(DATA_PATH, index=False)
                            st.success(f"↩️ Reverted to original price ₹{row['Original Price']} for {row['ProductName']}")
                            st.rerun()
                        except PermissionError:
                            st.warning("⚠️ Cannot write to file. Please close the Excel file and try again.")
else:
    st.info("✅ No low-confidence products to manually review.")
