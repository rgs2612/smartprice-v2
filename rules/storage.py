import os
import json

RULES_FILE = os.path.join("rules", "rules.json")

DEFAULT_RULES = [
    {
        "field": "Stock Level",
        "condition": "<",
        "value": 30,
        "action": "decrease",
        "adjustment": 5
    },
    {
        "field": "Demand",
        "condition": ">",
        "value": 80,
        "action": "increase",
        "adjustment": 10
    }
]

def load_rules():
    if not os.path.exists(RULES_FILE):
        print("🔧 rules.json not found — creating default rules.")
        os.makedirs("rules", exist_ok=True)
        with open(RULES_FILE, "w") as f:
            json.dump(DEFAULT_RULES, f, indent=2)
        return DEFAULT_RULES
    with open(RULES_FILE, "r") as f:
        return json.load(f)

def save_rules(rules):
    with open(RULES_FILE, "w") as f:
        json.dump(rules, f, indent=2)
