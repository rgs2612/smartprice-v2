import json

def load_ai_overrides(path="data/ai_overrides.json"):
    try:
        with open(path, "r") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return []

def save_ai_override(product_id, new_price, reason):
    overrides = load_ai_overrides()
    overrides = [o for o in overrides if o["product_id"] != product_id]
    overrides.append({
        "product_id": product_id,
        "new_price": new_price,
        "reason": reason,
        "OverrideType": "AI Recommended"
    })
    with open("data/ai_overrides.json", "w") as f:
        json.dump(overrides, f, indent=2)
