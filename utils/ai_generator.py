import json
from datetime import datetime
import random

def generate_ai_recommended_prices(df):
    overrides = []
    for _, row in df.iterrows():
        pid = row["ProductID"]
        our_price = row["Our Price"]
        demand = row["Demand"]
        stock = row["Stock Level"]

        # Simple mock AI logic: increase price if demand high
        if demand > 60 and stock > 10:
            ai_price = round(our_price * 1.05, 2)
            confidence = round(random.uniform(70, 95), 2)
        elif stock < 5:
            ai_price = round(our_price * 0.95, 2)
            confidence = round(random.uniform(60, 75), 2)
        else:
            continue

        overrides.append({
            "product_id": pid,
            "ai_price": ai_price,
            "confidence": confidence
        })

    with open("data/ai_scheduled.json", "w") as f:
        json.dump(overrides, f, indent=2)

    print(f"✅ AI recommended overrides written: {len(overrides)}")
