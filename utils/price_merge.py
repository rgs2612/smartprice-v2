# utils/price_merge.py

from utils.override_handler import apply_overrides
from utils.rules_override_handler import apply_rule_overrides

def apply_all_overrides(df):
    df = apply_overrides(df)            # Manual overrides from scheduled_changes.json
    df = apply_rule_overrides(df)       # Rule-based overrides from rule_scheduled_changes.json
    return df
