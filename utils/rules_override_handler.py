# utils/rules_override_handler.py
import json

def load_rule_scheduled_overrides(path="data/rules_scheduled_changes.json"):
    try:
        with open(path, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return []

def save_rule_scheduled_overrides(overrides, path="data/rules_scheduled_changes.json"):
    with open(path, "w") as f:
        json.dump(overrides, f, indent=2)
