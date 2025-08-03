import json
import pandas as pd

# Load mock product data
try:
    df = pd.read_excel("data/mock_product_data.xlsx")
    mock_ids = set(df["ProductID"].astype(str).unique())
except Exception as e:
    print(f"❌ Failed to load mock product data: {e}")
    exit()

# Load override product IDs
override_ids = set()

for file in ["data/rule_scheduled_changes.json", "data/ai_scheduled.json"]:
    try:
        with open(file, "r") as f:
            data = json.load(f)
            file_ids = {str(entry["product_id"]) for entry in data}
            print(f"{file}: {len(file_ids)} product_ids")
            override_ids.update(file_ids)
    except Exception as e:
        print(f"{file}: ❌ ERROR -> {e}")

# Compare
missing_ids = override_ids - mock_ids
print(f"\n🧩 ProductIDs in override files but missing from mock data: {len(missing_ids)}")
if missing_ids:
    print("Sample missing IDs:")
    print(sorted(list(missing_ids))[:10])
