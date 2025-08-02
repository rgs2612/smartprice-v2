# data/fix_missing_columns.py
import pandas as pd
import numpy as np

# Load product data
df = pd.read_excel("data/mock_product_data.xlsx")

num_rows = len(df)

# 1. Random stock level (Inventory)
df["Stock Level"] = np.random.randint(10, 100, size=num_rows)

# 2. Random demand
df["Demand"] = np.random.randint(30, 100, size=num_rows)

# 3. Competitor price (mean of Amazon, Flipkart, Croma)
df["Competitor Price"] = df[["Amazon Price", "Flipkart Price", "Croma Price"]].min(axis=1)

# 4. Confidence Score (0.65 to 0.99 range)
df["Confidence Score"] = np.round(np.random.uniform(0.65, 0.99, size=num_rows), 2)

# 5. Forecast Demand (Demand + random offset)
df["Forecast Demand"] = df["Demand"] + np.random.randint(2, 15, size=num_rows)

# 6. Our Price (min competitor + ₹1000 mock logic)
df["Our Price"] = df[["Amazon Price", "Flipkart Price", "Croma Price"]].min(axis=1) + 1000

# 7. AI Optimal Price (mean of min + average competitor price)
df["AI Optimal Price"] = (
    df[["Amazon Price", "Flipkart Price", "Croma Price"]].min(axis=1) +
    df[["Amazon Price", "Flipkart Price", "Croma Price"]].mean(axis=1)
) / 2
df["AI Optimal Price"] = df["AI Optimal Price"].round(0)

# Save updated data
df.to_excel("data/mock_product_data.xlsx", index=False)
print("✅ Missing columns added with varying values and formatted prices!")
