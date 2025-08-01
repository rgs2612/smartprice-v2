import os
import json
from datetime import datetime

def save_override(product, new_price, reason, expires_on):
    override = {
        "product": product,
        "new_price": new_price,
        "reason": reason,
        "expires_on": expires_on
    }

    try:
        with open("data/scheduled_changes.json", "r") as f:
            data = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        data = []

    data.append(override)

    with open("data/scheduled_changes.json", "w") as f:
        json.dump(data, f, indent=2)
