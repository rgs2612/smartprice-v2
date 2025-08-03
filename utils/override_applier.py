import json
from datetime import datetime
import pandas as pd

MANUAL_OVERRIDE_FILE = "data/scheduled_changes.json"
RULE_OVERRIDE_FILE = "data/rule_scheduled_changes.json"
AI_OVERRIDE_FILE = "data/ai_scheduled.json"

def apply_all_overrides(df):
    df = df.copy()
    now = datetime.now()

    def safe_load(file):
        try:
            with open(file, "r") as f:
                return json.load(f)
        except:
            return []

    manual = safe_load(MANUAL_OVERRIDE_FILE)
    rules = safe_load(RULE_OVERRIDE_FILE)
    ai = safe_load(AI_OVERRIDE_FILE)

    # Step 1: Manual Overrides
    for ovr in manual:
        try:
            pid = ovr["product_id"]
            new_price = ovr["new_price"]
            start = datetime.strptime(ovr["scheduled_for"], "%Y-%m-%d %H:%M:%S")
            end = datetime.strptime(ovr["expires_on"], "%Y-%m-%d %H:%M:%S")

            if start <= now <= end:
                mask = df["ProductID"] == pid
                df.loc[mask, "Price"] = new_price
                df.loc[mask, "Our Price"] = round(new_price)
                df.loc[mask, "OverrideType"] = "Manual"
        except Exception as e:
            print(f"[Manual Override Error] {e}")

    # Step 2: Rule-Based Overrides
    for ovr in rules:
        try:
            pid = ovr["product_id"]
            new_price = ovr["new_price"]
            start = datetime.strptime(ovr["scheduled_for"], "%Y-%m-%d %H:%M:%S")
            end = datetime.strptime(ovr["expires_on"], "%Y-%m-%d %H:%M:%S")

            if start <= now <= end:
                mask = (df["ProductID"] == pid) & (
                    df["OverrideType"].isna() | (df["OverrideType"] == "None")
                )
                df.loc[mask, "Price"] = new_price
                df.loc[mask, "Our Price"] = round(new_price)
                df.loc[mask, "OverrideType"] = "Rule-Based"
        except Exception as e:
            print(f"[Rule Override Error] {e}")

    # Step 3: AI Recommendations (auto-applied)
    for ovr in ai:
        try:
            pid = ovr["product_id"]
            new_price = ovr["ai_price"]
            confidence = ovr.get("confidence", None)

            mask = (df["ProductID"] == pid) & (
                df["OverrideType"].isna() | (df["OverrideType"] == "None")
            )
            df.loc[mask, "Price"] = round(new_price)
            df.loc[mask, "Our Price"] = round(new_price)
            df.loc[mask, "Confidence Score"] = confidence
            df.loc[mask, "OverrideType"] = "AI Recommended"
        except Exception as e:
            print(f"[AI Recommendation Error] {e}")

    return df
