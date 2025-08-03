from datetime import datetime
import pandas as pd
from utils.override_handler import load_scheduled_overrides
from utils.rules_override_handler import load_rule_scheduled_overrides
from utils.ai_override_handler import load_ai_overrides

def apply_overrides(df: pd.DataFrame) -> pd.DataFrame:
    now = datetime.now()

    manual = load_scheduled_overrides()
    rule_based = load_rule_scheduled_overrides()
    ai_recommended = load_ai_overrides()

    overrides_applied = {"Manual": 0, "Rule-Based": 0, "AI Recommended": 0}

    all_overrides = []

    for override in manual:
        if override["product_id"] in df["ProductID"].values:
            start = datetime.fromisoformat(override["scheduled_for"])
            end = datetime.fromisoformat(override["expires_on"])
            if start <= now <= end:
                all_overrides.append(override)

    for override in rule_based:
        if override["product_id"] in df["ProductID"].values:
            start = datetime.fromisoformat(override["scheduled_for"])
            end = datetime.fromisoformat(override["expires_on"])
            if start <= now <= end:
                all_overrides.append(override)

    for override in ai_recommended:
        if override["product_id"] in df["ProductID"].values:
            all_overrides.append(override)

    for override in all_overrides:
        product_id = override["product_id"]
        new_price = override["new_price"]
        override_type = override.get("OverrideType", "Manual")
        mask = df["ProductID"] == product_id
        if mask.any():
            df.loc[mask, "Price"] = new_price
            df.loc[mask, "OverrideType"] = override_type
            overrides_applied[override_type] += 1

    return df, overrides_applied
