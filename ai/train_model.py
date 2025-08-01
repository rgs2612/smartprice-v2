# ai/train_model.py
import pandas as pd
import joblib
from sklearn.ensemble import RandomForestRegressor

# Load mock training data
df = pd.read_excel("data/mock_product_data.xlsx")

# Define features and target
features = df[["TrendScore", "Demand", "Stock Level", "Competitor Price"]]
target = df["Our Price"]  # or 'Revenue' if optimizing for profit

# Train model
model = RandomForestRegressor()
model.fit(features, target)

# Save model
joblib.dump(model, "ai/price_model.pkl")

print("✅ Model trained and saved.")
