import json
from datetime import datetime
from utils.rules_override_handler import load_rule_scheduled_overrides

def apply_overrides(df):
    now = datetime.now()

    # Load manual overrides
    try:
        with open("data/scheduled_changes.json", "r") as f:
            manual_overrides = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        manual_overrides = []

    # Load rule-based overrides
    try:
        rule_overrides = load_rule_scheduled_overrides()
    except (FileNotFoundError, json.JSONDecodeError):
        rule_overrides = []

    all_overrides = manual_overrides + rule_overrides

    # Track applied overrides
    updated_rows = []

    for override in all_overrides:
        product = override.get("product")
        new_price = override.get("new_price")
        reason = override.get("reason", "Manual Override")

        # Check expiration
        try:
            expires_on = datetime.strptime(override.get("expires_on"), "%Y-%m-%d %H:%M:%S")
            if now > expires_on:
                continue
        except Exception:
            continue  # Skip if invalid or missing date

        # Apply override to matching product
        for idx, row in df.iterrows():
            if row.get("ProductName") == product:
                df.at[idx, "Our Price"] = new_price
                df.at[idx, "AI Price"] = new_price
                df.at[idx, "Reason"] = reason
                df.at[idx, "override_applied"] = True
                updated_rows.append(idx)

    # Ensure override_applied column exists
    if "override_applied" not in df.columns:
        df["override_applied"] = False

    return df


import json

def load_scheduled_overrides(path="data/scheduled_changes.json"):
    try:
        with open(path, "r") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return []

def save_scheduled_overrides(overrides, path="data/scheduled_changes.json"):
    with open(path, "w") as f:
        json.dump(overrides, f, indent=2)
