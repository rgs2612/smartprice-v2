import pandas as pd
import streamlit as st

def apply_rules(df: pd.DataFrame, rules: list) -> pd.DataFrame:
    changed_rows = []
    debug_rows = []

    for rule in rules:
        try:
            condition = rule.get("condition")
            operator = rule.get("operator")
            value = float(rule.get("value", 0))
            action = rule.get("action")

            # ✅ Safe handling of action_value (can be None)
            action_value_raw = rule.get("action_value")
            try:
                action_value = float(action_value_raw) if action_value_raw is not None else 0.0
            except ValueError:
                action_value = 0.0

            df = df.copy()

            for idx, row in df.iterrows():
                our_price = row["Our Price"]
                match = False
                competitor_price = min(row["Amazon Price"], row["Flipkart Price"], row["Croma Price"])

                if condition == "Competitor Price":
                    diff_percent = ((competitor_price - our_price) / our_price) * 100

                    match = (
                        (operator == "equals" and abs(diff_percent) < 0.1)
                        or (operator == "falls below" and diff_percent < -value)
                        or (operator == "rises above" and diff_percent > value)
                        or (operator == "drops by" and diff_percent <= -value)
                    )

                elif condition == "Stock Level":
                    stock_level = row.get("Stock Level", 0)
                    match = (
                        (operator == "falls below" and stock_level < value)
                        or (operator == "rises above" and stock_level > value)
                    )

                elif condition == "Demand Spike":
                    demand = row.get("Demand", 0)
                    match = (
                        (operator == "rises above" and demand > value)
                        or (operator == "falls below" and demand < value)
                    )

                if match:
                    new_price = our_price
                    if action == "Match Competitor Price":
                        new_price = competitor_price
                    elif action == "Increase Price by %":
                        new_price = our_price * (1 + action_value / 100)
                    elif action == "Decrease Price by %":
                        new_price = our_price * (1 - action_value / 100)
                    elif action == "Set Fixed Price":
                        new_price = action_value

                    if new_price != our_price:
                        df.at[idx, "Our Price"] = round(new_price)
                        changed_rows.append(idx)

                        # Debug info
                        debug_rows.append({
                            "Product": row["ProductName"],
                            "Our Price": our_price,
                            "Competitor Price": competitor_price,
                            "Diff %": round(diff_percent, 2) if condition == "Competitor Price" else "-",
                            "Action": action,
                            "New Price": round(new_price)
                        })

        except Exception as e:
            st.warning(f"Error applying rule {rule}: {e}")

    return df, df.loc[changed_rows]
