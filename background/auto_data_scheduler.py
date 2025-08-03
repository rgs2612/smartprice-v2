import threading
import random
import uuid
import numpy as np
import time
import pandas as pd
import os
from datetime import datetime
import sys
import json

# Add root to path
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from utils.override_applier import apply_all_overrides


# Path to Excel file
DATA_FILE = "data/mock_product_data.xlsx"
LOG_FILE = "data/mock_data_generation_log.txt"

# Globals
auto_generation_enabled = False
generation_thread = None
interval_minutes = 5  # default

def generate_mock_product_data():
    """Generate fresh mock data."""
    # Sample mock data logic (replace with your real generator)

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
    return df

def write_log(message):
    with open(LOG_FILE, "a") as f:
        f.write(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - {message}\n")

def clear_old_overrides():
    print(">> Running auto_data_scheduler.py")

    override_files = [
        "data/rule_scheduled_changes.json",
        "data/ai_scheduled.json"
    ]
    for file in override_files:
        try:
            with open(file, "w") as f:
                json.dump([], f)  # ✅ Requires json to be imported
            print(f"✅ Cleared {file} with []")
        except Exception as e:
            print(f"❌ Failed to clear {file}: {e}")



from utils.rule_generator import generate_rule_based_overrides
from utils.ai_generator import generate_ai_recommended_prices

def generate_and_save_data():
    clear_old_overrides()  # Step 1
    df = generate_mock_product_data()  # Step 2
    generate_rule_based_overrides(df)  # Step 3: Add rule overrides
    generate_ai_recommended_prices(df)  # Step 4: Add AI recommendations
    df = apply_all_overrides(df)  # Step 5
    df.to_excel(DATA_FILE, index=False)  # Step 6
    write_log("Mock data generated and overrides applied.")
    print("✅ New mock data generated with overrides applied.")



def _run_scheduler():
    global auto_generation_enabled, generation_thread

    if not auto_generation_enabled:
        return

    generate_and_save_data()
    generation_thread = threading.Timer(interval_minutes * 60, _run_scheduler)
    generation_thread.start()

def start_auto_generation(interval_min=5):
    global auto_generation_enabled, interval_minutes, generation_thread

    interval_minutes = interval_min
    auto_generation_enabled = True
    if generation_thread is None or not generation_thread.is_alive():
        _run_scheduler()
    write_log(f"Auto generation started with interval {interval_min} minutes.")

def stop_auto_generation():
    global auto_generation_enabled, generation_thread

    auto_generation_enabled = False
    if generation_thread is not None:
        generation_thread.cancel()
        generation_thread = None
    write_log("Auto generation stopped.")

def is_running():
    return auto_generation_enabled
