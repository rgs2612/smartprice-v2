# utils/override_handler.py

import json
from datetime import datetime

def load_scheduled_overrides():
    try:
        with open("data/scheduled_changes.json", "r") as f:
            overrides = json.load(f)
        return overrides
    except (FileNotFoundError, json.JSONDecodeError):
        return []

def save_scheduled_overrides(overrides):
    with open("data/scheduled_changes.json", "w") as f:
        json.dump(overrides, f, indent=4, default=str)
        


def apply_overrides(df):
    try:
        with open("data/scheduled_changes.json", "r") as f:
            overrides = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return df

    now = datetime.now()
    updated_df = df.copy()

    for override in overrides:
        try:
            product_id = override.get("product_id")
            new_price = override.get("new_price")
            scheduled_for_str = override.get("scheduled_for")
            expires_on_str = override.get("expires_on")

            # Skip if required datetime fields are missing
            if not scheduled_for_str or not expires_on_str:
                print(f"Skipping override for product ID {product_id}: missing schedule dates.")
                continue

            scheduled_for = datetime.strptime(scheduled_for_str, "%Y-%m-%d %H:%M:%S")
            expires_on = datetime.strptime(expires_on_str, "%Y-%m-%d %H:%M:%S")

            # Apply override if within schedule window
            if scheduled_for <= now <= expires_on:
                mask = updated_df["ProductID"] == product_id
                updated_df.loc[mask, "Price"] = new_price
                updated_df.loc[mask, "OverrideType"] = "Manual"
        except Exception as e:
            print(f"Error applying override for product ID {product_id}: {e}")

    return updated_df
