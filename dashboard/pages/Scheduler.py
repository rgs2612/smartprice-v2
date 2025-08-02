import streamlit as st
import pandas as pd
from datetime import datetime

from utils.override_handler import load_scheduled_overrides, save_scheduled_overrides
from utils.rules_override_handler import load_rule_scheduled_overrides, save_rule_scheduled_overrides

st.title("📅 One-Time AI Scheduler")

# ----------------------
# Manual Scheduled Overrides
# ----------------------
st.subheader("📋 Scheduled Manual Overrides")
manual_overrides = load_scheduled_overrides()

if not manual_overrides:
    st.info("No manual overrides scheduled.")
else:
    df_manual = pd.DataFrame(manual_overrides)
    st.dataframe(df_manual)

# ----------------------
# Rule-Based Scheduled Overrides
# ----------------------
st.subheader("⚙️ Scheduled Rule-Based Updates")
rule_overrides = load_rule_scheduled_overrides()

if not rule_overrides:
    st.info("No rule-based scheduled updates.")
else:
    try:
        df_rules = pd.DataFrame(rule_overrides)

        # Optional column reordering
        display_cols = ["product", "new_price", "reason", "scheduled_for", "expires_on"]
        if all(col in df_rules.columns for col in display_cols):
            df_rules = df_rules[display_cols]

        st.dataframe(df_rules)
    except Exception as e:
        st.error(f"⚠️ Failed to display rule overrides: {e}")
        st.json(rule_overrides)  # fallback raw view

# ----------------------
# Run Scheduler Button
# ----------------------
st.markdown("### 🚀 Run Scheduler Now")

if st.button("Run Scheduler Now"):
    now = datetime.now()

    # ✅ Filter & keep only *not yet active* or *future* manual overrides
    updated_manual = []
    for override in manual_overrides:
        try:
            start = datetime.strptime(override["scheduled_for"], "%Y-%m-%d %H:%M:%S")
            end = datetime.strptime(override["expires_on"], "%Y-%m-%d %H:%M:%S")
            if start <= now <= end:
                st.success(f"✅ Manual Override applied for: {override['product']}")
            else:
                updated_manual.append(override)
        except Exception as e:
            st.warning(f"⚠️ Manual override error: {e}")

    save_scheduled_overrides(updated_manual)

    # ✅ Same logic for rule overrides
    updated_rules = []
    for override in rule_overrides:
        try:
            start = datetime.strptime(override["scheduled_for"], "%Y-%m-%d %H:%M:%S")
            end = datetime.strptime(override["expires_on"], "%Y-%m-%d %H:%M:%S")
            if start <= now <= end:
                st.success(f"✅ Rule Override applied for: {override['product']}")
            else:
                updated_rules.append(override)
        except Exception as e:
            st.warning(f"⚠️ Rule override error: {e}")

    save_rule_scheduled_overrides(updated_rules)

    st.info("🔄 Scheduler run completed. Reloading...")
    st.rerun()
