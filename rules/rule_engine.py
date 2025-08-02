import pandas as pd
from datetime import datetime
import streamlit as st
from utils.rules_override_handler import load_rule_scheduled_overrides, save_rule_scheduled_overrides

def apply_rules(df: pd.DataFrame, rules: list) -> pd.DataFrame:
    df = df.copy()
    changed_rows = []
    scheduled_updates = []
    now = datetime.now()

    for rule in rules:
        try:
            # Rule metadata
            condition = rule.get("condition")
            operator = rule.get("operator")
            value = float(rule.get("value", 0))
            action = rule.get("action")
            scheduled_for = datetime.strptime(rule.get("scheduled_for"), "%Y-%m-%d %H:%M:%S")
            expires_on = datetime.strptime(rule.get("expires_on"), "%Y-%m-%d %H:%M:%S")

            # Only apply active rules
            if not (scheduled_for <= now <= expires_on):
                continue

            # Handle action_value if needed
            try:
                action_value = float(rule.get("action_value", 0))
            except:
                action_value = 0.0

            for idx, row in df.iterrows():
                our_price = row.get("Our Price", 0)
                competitor_price = min(row["Amazon Price"], row["Flipkart Price"], row["Croma Price"])
                stock = row.get("Stock Level", 0)
                demand = row.get("Demand", 0)
                match = False

                # --- Matching Conditions ---
                if condition == "Competitor Price":
                    diff_percent = ((competitor_price - our_price) / our_price) * 100
                    match = (
                        (operator == "equals" and abs(diff_percent) < 0.1) or
                        (operator == "falls below" and diff_percent < -value) or
                        (operator == "rises above" and diff_percent > value) or
                        (operator == "drops by" and diff_percent <= -value)
                    )

                elif condition == "Stock Level":
                    match = (
                        (operator == "falls below" and stock < value) or
                        (operator == "rises above" and stock > value)
                    )

                elif condition == "Demand Spike":
                    match = (
                        (operator == "falls below" and demand < value) or
                        (operator == "rises above" and demand > value)
                    )

                # --- Apply Action ---
                if match:
                    new_price = our_price
                    reason = f"{condition} - {action}"

                    if action == "Match Competitor Price":
                        new_price = competitor_price
                    elif action == "Increase Price by %":
                        new_price = our_price * (1 + action_value / 100)
                    elif action == "Decrease Price by %":
                        new_price = our_price * (1 - action_value / 100)
                    elif action == "Set Fixed Price":
                        new_price = action_value

                    new_price = round(new_price)

                    if round(new_price) != round(our_price):
                        df.at[idx, "Our Price"] = new_price
                        df.at[idx, "AI Price"] = new_price
                        df.at[idx, "Reason"] = reason
                        df.at[idx, "override_applied"] = True
                        changed_rows.append(idx)

                        # Append to rule scheduler
                        scheduled_updates.append({
                            "product": row.get("ProductName"),
                            "new_price": new_price,
                            "reason": reason,
                            "scheduled_for": now.strftime("%Y-%m-%d %H:%M:%S"),
                            "expires_on": expires_on.strftime("%Y-%m-%d %H:%M:%S")
                        })

        except Exception as e:
            st.warning(f"⚠️ Error applying rule: {e}")

    # Ensure override_applied column exists
    if "override_applied" not in df.columns:
        df["override_applied"] = False

    # Save rule-based scheduled overrides
    if scheduled_updates:
        try:
            existing = load_rule_scheduled_overrides()
        except:
            existing = []

        updated = existing + scheduled_updates
        save_rule_scheduled_overrides(updated)

    return df, df.loc[changed_rows]
