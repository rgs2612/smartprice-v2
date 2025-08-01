import json
from datetime import datetime

def apply_overrides(df):
    try:
        with open("data/scheduled_changes.json", "r") as f:
            overrides = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return df

    now = datetime.now()
    updated_overrides = []

    for override in overrides:
        product = override.get("product")
        new_price = override.get("new_price")
        reason = override.get("reason", "")

        # Handle optional fields
        scheduled_str = override.get("scheduled_for")
        expires_str = override.get("expires_on")

        scheduled_for = (
            datetime.strptime(scheduled_str, "%Y-%m-%d %H:%M:%S")
            if scheduled_str else
            now  # If not scheduled, treat as immediate
        )

        expires_on = (
            datetime.strptime(expires_str, "%Y-%m-%d %H:%M:%S")
            if expires_str else
            datetime.max  # Never expires unless specified
        )

        # Apply override if in active window
        if scheduled_for <= now < expires_on:
            df.loc[df["ProductName"] == product, "Our Price"] = new_price
            df.loc[df["ProductName"] == product, "override_applied"] = True
            updated_overrides.append(override)
        elif now < scheduled_for:
            updated_overrides.append(override)  # keep future override

    # Update file to remove expired ones
    with open("data/scheduled_changes.json", "w") as f:
        json.dump(updated_overrides, f, indent=2)

    return df

import os

SCHEDULE_FILE = "data/scheduled_changes.json"

def load_scheduled_overrides():
    if not os.path.exists(SCHEDULE_FILE):
        return []
    with open(SCHEDULE_FILE, "r") as f:
        return json.load(f)

def save_scheduled_overrides(overrides):
    with open(SCHEDULE_FILE, "w") as f:
        json.dump(overrides, f, indent=2)
