import json
from datetime import datetime
import os

RULE_OVERRIDE_PATH = "data/rule_scheduled_changes.json"  # Ensure file name matches your actual path

def load_rule_scheduled_overrides():
    if not os.path.exists(RULE_OVERRIDE_PATH):
        return []
    try:
        with open(RULE_OVERRIDE_PATH, "r") as f:
            return json.load(f)
    except json.JSONDecodeError:
        return []

def save_rule_scheduled_overrides(overrides):
    with open(RULE_OVERRIDE_PATH, "w") as f:
        json.dump(overrides, f, indent=2)

def apply_rule_overrides(df):
    rule_overrides = load_rule_scheduled_overrides()
    now = datetime.now()
    updated_df = df.copy()

    for override in rule_overrides:
        try:
            product_id = override.get("product_id")
            new_price = override.get("new_price")
            start = override.get("scheduled_for")
            end = override.get("expires_on")

            # Validate both timestamps
            if not start or not end:
                print(f"Skipping override for {product_id}: missing timestamps.")
                continue

            # Parse datetime strings
            start_date = datetime.strptime(start, "%Y-%m-%d %H:%M:%S")
            end_date = datetime.strptime(end, "%Y-%m-%d %H:%M:%S")

            if start_date <= now <= end_date:
                mask = updated_df["ProductID"] == product_id
                updated_df.loc[mask, "Price"] = new_price
                updated_df.loc[mask, "OverrideType"] = "Rule-Based"
                updated_df.loc[mask, "Override Reason"] = override.get("reason", "Rule Triggered")
        except Exception as e:
            print(f"Error applying rule override for product ID {override.get('product_id')}: {e}")

    return updated_df
