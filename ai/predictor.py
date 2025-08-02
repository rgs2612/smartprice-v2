import joblib
import os
import numpy as np

# Load trained model
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

        # Predict using each tree in ensemble to estimate confidence
        predictions = [est.predict([features])[0] for est in model.estimators_]
        ai_price = np.mean(predictions)
        std_dev = np.std(predictions)
        confidence = 1 - (std_dev / ai_price) if ai_price > 0 else 0

        return round(ai_price, 2), round(confidence, 2)

    except Exception as e:
        return row["Our Price"], 0.0
