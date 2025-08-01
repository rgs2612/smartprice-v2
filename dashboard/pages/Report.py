import streamlit as st
from rules.rule_engine import apply_rules
from rules.storage import load_rules
from utils.data_loader import load_product_data

st.title("📊 Pricing Summary Report")

df = load_product_data()
rules = load_rules()

if rules:
    st.markdown("### 📋 Applied Rules:")
    for i, rule in enumerate(rules):
        st.markdown(f"**{i+1}.** IF `{rule['condition']}` → THEN `{rule['action']}`")

    st.markdown("---")
    result_df = apply_rules(df, rules)

    # Show side-by-side
    st.dataframe(result_df[["ProductName", "Our Price", "Rule Adjusted Price"]])

    # Download
    csv = result_df.to_csv(index=False)
    st.download_button("📥 Download Report as CSV", data=csv, file_name="pricing_report.csv")
else:
    st.info("No rules applied yet.")
