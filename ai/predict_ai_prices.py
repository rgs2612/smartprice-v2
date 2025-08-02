import pandas as pd
import joblib

# Load model and data
model = joblib.load("ai/ai_price_model.pkl")
df = pd.read_excel("data/mock_product_data.xlsx")

# Predict prices
features = df[["TrendScore", "Stock Level", "Demand", "Competitor Price"]]
df["AI Optimal Price"] = model.predict(features)

# Optional: Confidence Score (inverse of variance between competitors)
df["Confidence Score"] = 100 - abs(df["AI Optimal Price"] - df["Competitor Price"]) / df["Competitor Price"] * 100

# Save predictions
df.to_excel("data/mock_product_data.xlsx", index=False)
print("✅ AI Prices predicted and saved.")
