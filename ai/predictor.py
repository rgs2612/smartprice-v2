# ai/predictor.py
import joblib
import os

model_path = os.path.join(os.path.dirname(__file__), "price_model.pkl")
model = joblib.load(model_path)

def predict_optimal_price(row):
    try:
        features = [
            row["TrendScore"],
            row["Demand"],
            row["Stock Level"],
            min(row["Amazon Price"], row["Flipkart Price"], row["Croma Price"])
        ]
        return round(model.predict([features])[0], 2)
    except:
        return row["Our Price"]
