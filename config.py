import os
import sys

# Dynamically resolve and add project root to sys.path
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(BASE_DIR)

# Define paths to important files
DATA_PATH = os.path.join(BASE_DIR, "data", "mock_product_data.xlsx")
MODEL_PATH = os.path.join(BASE_DIR, "ai", "price_model.pkl")
RULES_PATH = os.path.join(BASE_DIR, "rules", "rules.json")
SCHEDULE_PATH = os.path.join(BASE_DIR, "data", "scheduled_changes.json")
