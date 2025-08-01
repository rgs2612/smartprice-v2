import pandas as pd
import numpy as np

np.random.seed(42)
brands = ["Samsung", "Apple", "OnePlus", "Nothing", "Google", "Motorola"]
models = ["S23", "14", "Nord", "CMF 2", "Pixel 8", "Edge 40"]

products = [f"{np.random.choice(brands)} {np.random.choice(models)}" for _ in range(100)]

df = pd.DataFrame({
    "ProductName": products,
    "TrendScore": np.random.randint(60, 100, size=100),
    "Amazon Price": np.random.randint(30000, 80000, size=100),
    "Flipkart Price": np.random.randint(30000, 80000, size=100),
    "Croma Price": np.random.randint(30000, 80000, size=100)
})

# Your system price (before AI/rules)
df["Our Price"] = (df["Amazon Price"] + df["Flipkart Price"] + df["Croma Price"]) // 3

df.to_excel("data/mock_product_data.xlsx", index=False)
print("✅ mock_product_data.xlsx generated!")
