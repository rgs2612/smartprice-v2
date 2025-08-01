import streamlit as st
import pandas as pd

from utils.data_loader import load_product_data
from rules.rule_engine import apply_rules
from rules.storage import save_rules, load_rules

st.title("📋 Pricing Rule Builder")

# --- Initialize Session State ---
if "rules" not in st.session_state:
    st.session_state.rules = load_rules()

    # 🔁 Backward compatibility for old-format rules
    for rule in st.session_state.rules:
        if "operator" not in rule:
            try:
                # --- Legacy Condition Parser ---
                cond_parts = rule.get("condition", "").rsplit(" ", 2)
                if len(cond_parts) == 3:
                    rule["condition"] = cond_parts[0]
                    rule["operator"] = cond_parts[1]
                    try:
                        rule["value"] = float(cond_parts[2].replace("%", ""))
                    except ValueError:
                        rule["value"] = 0.0
                else:
                    rule["value"] = 0.0

                # --- Legacy Action Parser ---
                action_parts = rule.get("action", "").rsplit(" ", 1)
                if len(action_parts) == 2:
                    rule["action"] = action_parts[0]
                    try:
                        rule["action_value"] = float(action_parts[1].replace("%", ""))
                    except ValueError:
                        rule["action_value"] = 0
                else:
                    rule["action_value"] = 0

            except Exception as e:
                st.warning(f"❌ Failed to migrate old rule: {rule} — Error: {e}")

# --- UI to Create Rules ---
st.markdown("### ➕ Define New Rule")

col1, col2, col3 = st.columns([2, 1, 2])
with col1:
    condition_field = st.selectbox("When", [
        "Competitor Price", "Stock Level", "Demand Spike"
    ])

with col2:
    operator = st.selectbox("Operator", [
        "drops by", "rises above", "falls below", "equals"
    ])

with col3:
    value = st.number_input("Value (%)", min_value=0.0, max_value=100.0, value=10.0)

action = st.selectbox("Then", [
    "Match Competitor Price",
    "Increase Price by %",
    "Decrease Price by %",
    "Set Fixed Price"
])

action_value = None
if "by %" in action:
    action_value = st.slider("How much %?", min_value=1, max_value=50, value=5)
elif action == "Set Fixed Price":
    action_value = st.number_input("Enter Fixed Price", min_value=1, value=1000)

# --- Add Rule Button ---
if st.button("➕ Add Rule"):
    rule = {
        "condition": condition_field,
        "operator": operator,
        "value": value,
        "action": action,
        "action_value": action_value
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
            try:
                condition_str = f"{rule['condition']} {rule['operator']} {rule['value']}%"
                action_str = rule['action']
                if "by %" in rule['action']:
                    action_str += f" {rule.get('action_value', '')}%"
                elif rule['action'] == "Set Fixed Price":
                    action_str += f" {rule.get('action_value', '')}"
                st.markdown(f"**{i+1}.** IF {condition_str} → THEN {action_str}")
            except Exception as e:
                st.error(f"❌ Error displaying rule #{i+1}: {e}")
        with colB:
            if st.button("❌", key=f"delete_{i}"):
                st.session_state.rules.pop(i)
                save_rules(st.session_state.rules)
                st.rerun()
else:
    st.info("No rules defined yet.")

# --- Load Data ---
df = load_product_data()

# ✅ Add Competitor Price column before rule application
df["Competitor Price"] = df[["Amazon Price", "Flipkart Price", "Croma Price"]].min(axis=1)

# --- Apply Rules ---
if st.session_state.rules:
    adjusted_df, changed_products = apply_rules(df.copy(), st.session_state.rules)

    st.markdown("## 📊 Products Affected by Rules")
    if not changed_products.empty:
        st.success(f"✅ {len(changed_products)} products updated by rules")
        st.dataframe(changed_products)
       
    else:
        st.info("ℹ️ No product prices were changed by the current rules.")
