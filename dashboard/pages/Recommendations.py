import streamlit as st
import pandas as pd
import joblib
import os
import json

# File paths
DATA_PATH = "data/mock_product_data.xlsx"
MODEL_PATH = "ai/ai_price_model.pkl"
AI_JSON_PATH = "data/ai_scheduled.json"

st.set_page_config(page_title="🤖 AI Pricing Recommendations", layout="wide")
st.title("🤖 AI Pricing Recommendations")

# Load product data
df = pd.read_excel(DATA_PATH)

# Load AI model
model = joblib.load(MODEL_PATH)

# Predict AI Price & Confidence
features = ["TrendScore", "Stock Level", "Demand", "Competitor Price"]
df["AI Price"] = model.predict(df[features]).round(2)
df["Confidence Score"] = (100 - abs(df["AI Price"] - df["Competitor Price"]) / df["Competitor Price"] * 100).round(2)

# Load existing AI overrides
if os.path.exists(AI_JSON_PATH):
    with open(AI_JSON_PATH, "r") as f:
        ai_overrides = json.load(f)
else:
    ai_overrides = []

# Mapping for fast lookup
ai_override_map = {entry["product_id"]: entry for entry in ai_overrides}

# Set override types
df["OverrideType"] = df["ProductID"].apply(
    lambda x: "AI Recommended" if x in ai_override_map else None
)

# Filter out products already overridden by Manual or Rule-Based (if needed)
excluded_ids = set()
# You can load manual/rule overrides and add to excluded_ids if needed

# Filter: Only products not already manually or rule overridden
filtered_df = df[~df["ProductID"].isin(excluded_ids)].copy()



st.markdown("---")
st.subheader("📋 AI Price Suggestions")

# Placeholder for dynamic messages
message_placeholder = st.empty()

# Sticky controls
col1, col2, col3 = st.columns(3)
select_all = col1.checkbox("✅ Select All", key="select_all_ai")
apply_clicked = col2.button("🚀 Apply Selected", key="apply_ai")
revert_clicked = col3.button("↩️ Revert Selected", key="revert_ai")

# State storage
selected_ids = []

# Show AI Recommendations
for _, row in filtered_df.iterrows():
    is_applied = row["ProductID"] in ai_override_map
    bg_color = "#dcfce7" if is_applied else ("#fff3cd" if row["Confidence Score"] < 70 else "#e0f7fa")

    with st.container():
        cols = st.columns([0.07, 0.93])
        checked = select_all or cols[0].checkbox("", key=f"chk_{row['ProductID']}")
        if checked:
            selected_ids.append(row["ProductID"])

        with cols[1]:
            applied_text = "<span style='color:green; font-weight:bold;'>(Applied)</span>" if is_applied else ""
            st.markdown(
                f"""
                <div style='padding:15px; border-radius:10px; background-color:{bg_color}; margin-bottom:10px; border:1px solid #ccc;'>
                    <div style='font-size:18px; font-weight:bold;'>{row['ProductName']} {applied_text}</div>
                    <div style='margin-top:5px;'>
                        <b>Our Price:</b> ₹{int(row['Our Price'])} &nbsp; → &nbsp;
                        <b>AI Price:</b> ₹{int(row['AI Price'])}
                    </div>
                    <div style='margin-top:3px;'>
                        <b>Confidence Score:</b> {row['Confidence Score']}% &nbsp; {"✅" if row['Confidence Score'] >= 70 else "⚠️"}
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )

# Apply selected AI recommendations
if apply_clicked and selected_ids:
    for pid in selected_ids:
        row = df[df["ProductID"] == pid].iloc[0]
        ai_override_map[pid] = {
            "product_id": pid,
            "ai_price": float(row["AI Price"]),
            "confidence": float(row["Confidence Score"]),
            "OverrideType": "AI Recommended"
        }

    with open(AI_JSON_PATH, "w") as f:
        json.dump(list(ai_override_map.values()), f, indent=2)

    message_placeholder.success("✅ Applied selected AI Recommendations.")
    st.rerun()

# Revert selected AI overrides
if revert_clicked and selected_ids:
    for pid in selected_ids:
        if pid in ai_override_map:
            del ai_override_map[pid]

    with open(AI_JSON_PATH, "w") as f:
        json.dump(list(ai_override_map.values()), f, indent=2)

    message_placeholder.warning("↩️ Reverted selected AI Recommendations.")
    st.rerun()
