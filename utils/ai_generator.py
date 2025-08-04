import json
import pandas as pd
import numpy as np

def generate_ai_recommended_prices(df):
    overrides = []

    # ✅ Ensure Confidence Score is numeric and normalized
    df["Confidence Score"] = pd.to_numeric(df["Confidence Score"], errors="coerce").fillna(0)
    if df["Confidence Score"].max() > 1:
        df["Confidence Score"] = df["Confidence Score"] / 100

    # ✅ Ensure Price Gap column exists
    if "Competitor Price" not in df.columns:
        df["Competitor Price"] = df[["Amazon Price", "Flipkart Price", "Croma Price"]].min(axis=1)
    df["Price Gap"] = abs(df["Our Price"] - df["Competitor Price"])

    for _, row in df.iterrows():
        pid = row["ProductID"]
        product_name = row["ProductName"]
        our_price = row["Our Price"]
        demand = row["Demand"]
        stock = row["Stock Level"]
        confidence = row["Confidence Score"]
        price_gap = row["Price Gap"]

        # Simple mock AI logic to generate AI Price
        if demand > 60 and stock > 10:
            ai_price = round(our_price * 1.05, 2)
        elif stock < 5:
            ai_price = round(our_price * 0.95, 2)
        else:
            ai_price = round(our_price * 1.02, 2)

        # ✅ Eligibility check for auto-apply
        if confidence >= 0.70 and stock >= 5 and price_gap < 2000:
            overrides.append({
                "product_id": pid,
                "product_name": product_name,
                "ai_price": ai_price,
                "confidence": round(confidence, 4),
                "OverrideType": "AI Recommended (Auto)"
            })

    # --- Save to JSON
    with open("data/ai_scheduled.json", "w") as f:
        json.dump(overrides, f, indent=2)

    print(f"✅ AI recommended overrides written: {len(overrides)}")
