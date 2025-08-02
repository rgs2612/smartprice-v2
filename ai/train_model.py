import pandas as pd
from sklearn.ensemble import RandomForestRegressor
import joblib

# Load data
df = pd.read_excel("data/mock_product_data.xlsx")

# Define features and target
features = df[["TrendScore", "Stock Level", "Demand", "Competitor Price"]]
target = df["Our Price"]

# Train model
model = RandomForestRegressor(n_estimators=100, random_state=42)
model.fit(features, target)

# Save model
joblib.dump(model, "ai/ai_price_model.pkl")
print("✅ Model trained and saved.")
