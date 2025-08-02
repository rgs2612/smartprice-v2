# utils/price_applier.py
import pandas as pd

def apply_prices(df: pd.DataFrame, path="data/mock_product_data.xlsx") -> None:
    try:
        # Load existing data
        full_df = pd.read_excel(path)

        # Update only rows that match ProductName
        for _, row in df.iterrows():
            mask = full_df["ProductName"] == row["ProductName"]
            full_df.loc[mask, "Our Price"] = row["AI Optimal Price"]

        # Save back to Excel
        full_df.to_excel(path, index=False)
        print("✅ Prices updated in mock_product_data.xlsx")

    except Exception as e:
        print(f"❌ Failed to apply prices: {e}")
