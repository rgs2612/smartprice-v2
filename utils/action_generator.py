# utils/action_generator.py
import pandas as pd
import numpy as np

def generate_action(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()

    # Ensure required columns exist
    if "Our Price" not in df.columns or "Competitor Price" not in df.columns:
        raise ValueError("Missing pricing columns in input DataFrame.")

    df["Price Gap"] = (df["Our Price"] - df["Competitor Price"]).abs()

    # Initialize Action column
    df["Action"] = "No Action"

    # 🔴 Low Stock
    df.loc[df["Stock Level"] < 5, "Action"] = "Lock Pricing / Notify Reorder"

    # ⚠️ Price Gap > ₹2000
    df.loc[df["Price Gap"] > 2000, "Action"] = "Review Pricing (Gap > ₹2000)"

    # 😬 Low AI Confidence
    df.loc[df["Confidence Score"] < 0.7, "Action"] = "Manual Review (Low Confidence)"

    return df
