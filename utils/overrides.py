import os
import json
from datetime import datetime

def save_override(product_id, new_price, reason, scheduled_for, expires_on):
    override = {
        "product_id": product_id,
        "new_price": new_price,
        "reason": reason,
        "scheduled_for": scheduled_for.strftime("%Y-%m-%d %H:%M:%S"),
        "expires_on": expires_on.strftime("%Y-%m-%d %H:%M:%S")
    }

    try:
        with open("data/scheduled_changes.json", "r") as f:
            data = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        data = []

    data.append(override)

    with open("data/scheduled_changes.json", "w") as f:
        json.dump(data, f, indent=2)
