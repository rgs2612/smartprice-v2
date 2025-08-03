import streamlit as st
import pandas as pd
from datetime import datetime
from utils.override_handler import load_scheduled_overrides, save_scheduled_overrides
from utils.rules_override_handler import load_rule_scheduled_overrides, save_rule_scheduled_overrides
from utils.data_loader import load_product_data

DATA_PATH = "data/mock_product_data.xlsx"

st.title("📅 One-Time AI Scheduler")

# Load current product data
df = load_product_data()

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
        display_cols = ["product_id", "new_price", "reason", "scheduled_for", "expires_on"]
        df_rules = df_rules[display_cols] if all(col in df_rules.columns for col in display_cols) else df_rules
        st.dataframe(df_rules)
    except Exception as e:
        st.error(f"⚠️ Failed to display rule overrides: {e}")
        st.json(rule_overrides)  # fallback raw display

# ----------------------
# Run Scheduler Button
# ----------------------
st.markdown("### 🚀 Run Scheduler Now")
if st.button("Run Scheduler Now"):
    now = datetime.now()

    # Apply manual overrides
    updated_manual = []
    for override in manual_overrides:
        try:
            start = datetime.strptime(override["scheduled_for"], "%Y-%m-%d %H:%M:%S")
            end = datetime.strptime(override["expires_on"], "%Y-%m-%d %H:%M:%S")
            if start <= now <= end:
                pid = override["product_id"]
                df.loc[df["ProductID"] == pid, "Our Price"] = override["new_price"]
                df.loc[df["ProductID"] == pid, "Reason"] = override["reason"]
                df.loc[df["ProductID"] == pid, "override_applied"] = True
                st.success(f"✅ Manual Override applied for Product ID: {pid}")
            else:
                updated_manual.append(override)
        except Exception as e:
            st.error(f"Error processing manual override: {e}")

    save_scheduled_overrides(updated_manual)

    # Apply rule-based overrides
    updated_rules = []
    for override in rule_overrides:
        try:
            start = datetime.strptime(override["scheduled_for"], "%Y-%m-%d %H:%M:%S")
            end = datetime.strptime(override["expires_on"], "%Y-%m-%d %H:%M:%S")
            if start <= now <= end:
                pid = override["product_id"]
                df.loc[df["ProductID"] == pid, "Our Price"] = override["new_price"]
                df.loc[df["ProductID"] == pid, "Reason"] = override["reason"]
                df.loc[df["ProductID"] == pid, "override_applied"] = True
                st.success(f"✅ Rule Override applied for Product ID: {pid}")
            else:
                updated_rules.append(override)
        except Exception as e:
            st.error(f"Error processing rule override: {e}")

    save_rule_scheduled_overrides(updated_rules)

    # Save changes to Excel
    try:
        df.to_excel(DATA_PATH, index=False)
        st.success("✅ Price changes saved to Excel.")
    except PermissionError:
        st.warning("⚠️ Cannot save to Excel. Please close the file and try again.")

    st.rerun()
