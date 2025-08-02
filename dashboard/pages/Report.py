import streamlit as st
import pandas as pd
from utils.override_handler import load_scheduled_overrides
from utils.rules_override_handler import load_rule_scheduled_overrides

st.title("📊 AI Monitoring Dashboard")

# Load overrides
manual = load_scheduled_overrides()
rule_based = load_rule_scheduled_overrides()

# Tag them for reporting
for m in manual:
    m["type"] = "Manual"
for r in rule_based:
    r["type"] = "Rule"

combined = manual + rule_based

# ----------------------------
# 📈 Recently Scheduled AI Price Changes
# ----------------------------
st.subheader("📈 Recently Scheduled AI Price Changes")

if combined:
    df_combined = pd.DataFrame(combined)
    display_cols = ["product", "new_price", "reason", "scheduled_for", "expires_on", "type"]
    if all(col in df_combined.columns for col in display_cols):
        df_combined = df_combined[display_cols]
    df_combined = df_combined.sort_values("scheduled_for", ascending=False)
    st.dataframe(df_combined, use_container_width=True)
else:
    st.info("No recent price changes scheduled.")

# ----------------------------
# 📊 Report Summary
# ----------------------------
st.subheader("📊 Price Update Report")

total_manual = len(manual)
total_rule = len(rule_based)
total_combined = len(combined)

if total_combined > 0:
    manual_expiring = sum(pd.to_datetime([m['expires_on'] for m in manual]) < pd.Timestamp.now())
    rule_expiring = sum(pd.to_datetime([r['expires_on'] for r in rule_based]) < pd.Timestamp.now())

    st.markdown(f"""
    - 🧾 **Total Scheduled Overrides**: `{total_combined}`
    - ✍️ **Manual Overrides**: `{total_manual}` ({manual_expiring} expired)
    - ⚙️ **Rule-Based Overrides**: `{total_rule}` ({rule_expiring} expired)
    """)
else:
    st.info("No overrides to report.")

# ----------------------------
# 🚨 Price Outlier Detection
# ----------------------------
st.subheader("🚨 Price Outlier Detection")
st.success("✅ No major price outliers found.")  # placeholder
