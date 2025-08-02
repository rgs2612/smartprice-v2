import streamlit as st
import pandas as pd
from datetime import datetime, time, date
import json

from utils.data_loader import load_product_data
from rules.rule_engine import apply_rules
from rules.storage import save_rules, load_rules
from utils.rules_override_handler import load_rule_scheduled_overrides, save_rule_scheduled_overrides

st.title("📋 Pricing Rule Builder")

# --- Initialize Session State ---
if "rules" not in st.session_state:
    st.session_state.rules = load_rules()

# --- UI to Create Rules ---
st.markdown("### ➕ Define New Rule")

col1, col2, col3 = st.columns([2, 1, 2])
with col1:
    condition_field = st.selectbox("When", ["Competitor Price", "Stock Level", "Demand Spike"])

with col2:
    operator = st.selectbox("Operator", ["drops by", "rises above", "falls below", "equals"])

with col3:
    value = st.number_input("Value (%)", min_value=0.0, max_value=100.0, value=10.0)

action = st.selectbox("Then", [
    "Match Competitor Price",
    "Increase Price by %",
    "Decrease Price by %",
    "Set Fixed Price"
])

# Show slider/input depending on action type
action_value = None
if "by %" in action:
    action_value = st.slider("How much %?", min_value=1, max_value=50, value=5)
elif action == "Set Fixed Price":
    action_value = st.number_input("Enter Fixed Price", min_value=1, value=1000)

# Schedule start
st.markdown("### 🕒 Schedule Time")
schedule_date = st.date_input("Start Date", value=date.today())
schedule_time = st.time_input("Start Time", value=datetime.now().time())
scheduled_for = datetime.combine(schedule_date, schedule_time).strftime("%Y-%m-%d %H:%M:%S")

# Expiry
st.markdown("### ⏳ Expiry Time")
expire_date = st.date_input("Expire Date", value=date.today())
expire_time = st.time_input("Expire Time", value=(datetime.now().replace(hour=23, minute=59)).time())
expires_on = datetime.combine(expire_date, expire_time).strftime("%Y-%m-%d %H:%M:%S")

# --- Add Rule Button ---
if st.button("➕ Add Rule"):
    rule = {
        "condition": condition_field,
        "operator": operator,
        "value": value,
        "action": action,
        "action_value": action_value,
        "scheduled_for": scheduled_for,
        "expires_on": expires_on
    }
    st.session_state.rules.append(rule)
    save_rules(st.session_state.rules)
    st.success("✅ Rule added and saved!")

# --- Display Active Rules ---
st.markdown("## 🧾 Active Pricing Rules")
if st.session_state.rules:
    for i, rule in enumerate(st.session_state.rules):
        colA, colB = st.columns([10, 1])
        with colA:
            st.markdown(
                f"**{i+1}.** IF `{rule['condition']} {rule['operator']} {rule['value']}%` "
                f"→ THEN `{rule['action']} {str(rule['action_value']) if rule['action_value'] is not None else ''}`  \n"
                f"⏱️ {rule.get('scheduled_for')} → ⌛ {rule.get('expires_on')}"
            )
        with colB:

            if st.button("❌", key=f"delete_{i}"):
                # Remove the rule from memory and save
                deleted_rule = st.session_state.rules.pop(i)
                save_rules(st.session_state.rules)

                # Clean up corresponding overrides
                try:
                    all_overrides = load_rule_scheduled_overrides()
                    cleaned_overrides = [
                        o for o in all_overrides
                        if not (o.get("reason", "").startswith(deleted_rule["condition"]) and
                                o.get("reason", "").endswith(deleted_rule["action"]))
                    ]
                    save_rule_scheduled_overrides(cleaned_overrides)
                except Exception as e:
                    st.warning(f"⚠️ Failed to remove related overrides: {e}")

                st.rerun()
                
else:
    st.info("No rules defined yet.")

# --- Load Product Data ---
df = load_product_data()

# Add competitor price reference
df["Competitor Price"] = df[["Amazon Price", "Flipkart Price", "Croma Price"]].min(axis=1)

# --- Apply Rules ---
if st.session_state.rules:
    adjusted_df, changed_products = apply_rules(df.copy(), st.session_state.rules)

    st.markdown("## 📊 Products Affected by Rules")
    if not changed_products.empty:
        st.success(f"✅ {len(changed_products)} products updated by rules")

        # Optional additional columns for display clarity
        display_cols = [
            "ProductName", "Our Price", "AI Suggested Price", "Competitor Price", 
            "Stock Level", "Demand", "Reason"
        ]
        display_df = changed_products[[col for col in display_cols if col in changed_products.columns]]
        st.dataframe(display_df)
    else:
        st.info("ℹ️ No product prices were changed by the current rules.")
