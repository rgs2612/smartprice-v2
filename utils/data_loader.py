import pandas as pd
import numpy as np
from config import DATA_PATH

def load_product_data():
    df = pd.read_excel(DATA_PATH)

    # ✅ Ensure required columns for rule engine exist
    if 'Stock Level' not in df.columns:
        df['Stock Level'] = np.random.randint(10, 100, size=len(df))

    if 'Demand' not in df.columns:
        df['Demand'] = np.random.randint(50, 100, size=len(df))

    if 'Competitor Price' not in df.columns:
        df["Competitor Price"] = df[["Amazon Price", "Flipkart Price", "Croma Price"]].min(axis=1)

        # Unify AI price columns
    if "AI Suggested Price" in df.columns:
        df["AI Price"] = df["AI Suggested Price"].combine_first(df.get("AI Price"))
        df.drop(columns=["AI Suggested Price"], inplace=True)

    if "AI Optimal Price" in df.columns:
        df["AI Price"] = df["AI Optimal Price"].combine_first(df.get("AI Price"))
        df.drop(columns=["AI Optimal Price"], inplace=True)


    return df




