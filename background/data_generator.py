# background/data_generator.py

import pandas as pd
import random
import uuid
import numpy as np
import time
import json
import os
from datetime import datetime
import joblib

# --- File Paths ---
STATE_PATH = "data/generation_state.json"
CONFIG_PATH = "data/generation_config.json"
LOG_PATH = "data/generation_log.txt"
OUTPUT_PATH = "data/mock_product_data.xlsx"
AI_JSON_PATH = "data/ai_scheduled.json"
MODEL_PATH = "ai/ai_price_model.pkl"

def log(message):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(LOG_PATH, "a", encoding="utf-8") as f:
        f.write(f"[{timestamp}] {message}\n")

def initialize():
    if not os.path.exists(STATE_PATH):
        with open(STATE_PATH, "w") as f:
            json.dump({"status": "stopped"}, f)
    if not os.path.exists(CONFIG_PATH):
        with open(CONFIG_PATH, "w") as f:
            json.dump({"interval_minutes": 10}, f)
    if not os.path.exists(LOG_PATH):
        open(LOG_PATH, "a").close()

def generate_mock_data():
    brands = ["Samsung", "Apple", "Xiaomi", "Realme", "OnePlus"]
    models = ["S23", "14", "Nord", "CMF 2", "Pixel 8", "Edge 40"]
    products = []

    for _ in range(100):
        brand = random.choice(brands)
        model = random.choice(models)
        product_name = f"{brand} {model}"
        product_id = str(uuid.uuid4())[:8]
        base_price = random.randint(8000, 80000)

        product = {
            "ProductID": product_id,
            "ProductName": product_name,
            "TrendScore": round(random.uniform(30, 100), 2),
            "Stock Level": random.randint(0, 500),
            "Demand": round(random.uniform(10, 100), 2),
            "Amazon Price": random.randint(30000, 80000),
            "Flipkart Price": random.randint(30000, 80000),
            "Croma Price": random.randint(30000, 80000),
            "Our Price": round(base_price, 2),
            "Reason": "",
            "override_applied": False,
            "OverrideType": "",
            "AI Price": None
        }
        products.append(product)

    df = pd.DataFrame(products)
    df["Competitor Price"] = df[["Amazon Price", "Flipkart Price", "Croma Price"]].min(axis=1)
    df["Confidence Score"] = np.round(np.random.uniform(0.65, 0.99, size=len(df)), 2)
    df["Forecast Demand"] = df["Demand"] + np.random.randint(2, 15, size=len(df))

    # --- Apply AI Recommended Price ---
    if os.path.exists(MODEL_PATH):
        model = joblib.load(MODEL_PATH)
        features = ["TrendScore", "Stock Level", "Demand", "Competitor Price"]
        df["AI Price"] = model.predict(df[features]).round(2)

        ai_overrides = []
        for i, row in df.iterrows():
            if (
                row["Confidence Score"] >= 0.70 and
                row["Stock Level"] >= 5 and
                abs(row["Our Price"] - row["Competitor Price"]) <= 2000
            ):
                df.at[i, "Our Price"] = row["AI Price"]
                df.at[i, "Price"] = row["AI Price"]
                df.at[i, "override_applied"] = True
                df.at[i, "OverrideType"] = "ai recommended"
                df.at[i, "Reason"] = "AI Recommended based on confidence & price gap"

                ai_overrides.append({
                    "product_id": row["ProductID"],
                    "product_name": row["ProductName"],
                    "ai_price": float(row["AI Price"]),
                    "confidence": float(row["Confidence Score"]),
                    "OverrideType": "AI Recommended"
                })

        with open(AI_JSON_PATH, "w") as f:
            json.dump(ai_overrides, f, indent=2)

        log(f"🧠 {len(ai_overrides)} AI recommendations auto-applied.")

    # Sync Price column
    df["Price"] = df["Our Price"]
    df.to_excel(OUTPUT_PATH, index=False)
    log("✅ Mock product data generated.")
