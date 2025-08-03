import pandas as pd
import random
import uuid
import numpy as np

brands = ["Samsung", "Apple", "Xiaomi", "Realme", "OnePlus"]
models = ["S23", "14", "Nord", "CMF 2", "Pixel 8", "Edge 40"]

products = []

# Generate 100 mock products
for _ in range(100):
    brand = random.choice(brands)
    model = random.choice(models)
    product_name = f"{brand} {model}"
    product_id = str(uuid.uuid4())[:8]
    price = random.randint(8000, 80000)

    product = {
        "ProductID": product_id,
        "ProductName": product_name,
        "TrendScore": round(random.uniform(30, 100), 2),
        "Stock Level": random.randint(0, 500),
        "Demand": round(random.uniform(10, 100), 2),
        "Amazon Price": random.randint(30000, 80000),
        "Flipkart Price": random.randint(30000, 80000),
        "Croma Price": random.randint(30000, 80000),
        "Our Price": round(price, 2),
        "Reason": "",
        "override_applied": False
    }
    products.append(product)

# Create DataFrame
df = pd.DataFrame(products)

# Compute derived fields
df["Competitor Price"] = df[["Amazon Price", "Flipkart Price", "Croma Price"]].min(axis=1)
df["Confidence Score"] = np.round(np.random.uniform(65, 99, size=len(df)) / 100, 2)
df["Forecast Demand"] = df["Demand"] + np.random.randint(2, 15, size=len(df))

# Save to Excel
df.to_excel("data/mock_product_data.xlsx", index=False)
print("✅ Mock data with ProductID saved.")
