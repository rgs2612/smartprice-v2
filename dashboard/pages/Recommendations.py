import streamlit as st
import pandas as pd
import joblib
import os
import json

st.set_page_config(page_title="🤖 AI Pricing Recommendations", layout="wide")
st.title("🤖 AI Pricing Recommendations")

# --- File Paths ---
DATA_PATH = "data/mock_product_data.xlsx"
MODEL_PATH = "ai/ai_price_model.pkl"
AI_JSON_PATH = "data/ai_scheduled.json"

# --- Load Data ---
df = pd.read_excel(DATA_PATH)
model = joblib.load(MODEL_PATH)

# --- Generate AI Predictions ---
features = ["TrendScore", "Stock Level", "Demand", "Competitor Price"]
df["AI Price"] = model.predict(df[features]).round(2)
df["Price Gap"] = abs(df["Competitor Price"] - df["Our Price"])

# --- Load Existing AI Overrides ---
if os.path.exists(AI_JSON_PATH):
    with open(AI_JSON_PATH, "r") as f:
        try:
            raw_data = json.load(f)
            ai_overrides = [o for o in raw_data if isinstance(o, dict) and "product_id" in o]
        except json.JSONDecodeError:
            ai_overrides = []
else:
    ai_overrides = []

applied_ids = [o.get("product_id") for o in ai_overrides]

# --- Auto-Apply Eligible AI Recommendations ---
def is_eligible_auto_apply(row):
    return (
        row["Confidence Score"] >= 0.70 and
        row["Price Gap"] <= 2000 and
        row["Stock Level"] >= 5
    )

df["EligibleForAutoApply"] = df.apply(is_eligible_auto_apply, axis=1)

# Auto-apply if not already applied
for _, row in df[df["EligibleForAutoApply"]].iterrows():
    if row["ProductID"] not in applied_ids:
        ai_overrides.append({
            "product_id": row["ProductID"],
            "product_name": row["ProductName"],
            "ai_price": float(row["AI Price"]),
            "confidence": float(row["Confidence Score"]),
            "OverrideType": "AI Recommended"
        })

# Save updated override list
with open(AI_JSON_PATH, "w") as f:
    json.dump(ai_overrides, f, indent=2)

# --- Mark Applied ---
df["Applied"] = df["ProductID"].isin([o.get("product_id") for o in ai_overrides])
df["OverrideType"] = df["Applied"].apply(lambda x: "AI Recommended" if x else None)

# --- Filter UI ---
st.markdown("### 🔍 Filter Recommendations")
category = st.selectbox("Select Filter", ["Low Confidence", "Low Stock", "Price Gap > ₹2000", "High Confidence"])

def filter_by_category(df, category):
    if category == "Low Confidence":
        return df[df["Confidence Score"] < 0.70]
    elif category == "Low Stock":
        return df[df["Stock Level"] < 5]
    elif category == "Price Gap > ₹2000":
        return df[df["Price Gap"] > 2000]
    elif category == "High Confidence":
        return df[
            (df["Confidence Score"] >= 0.70) &
            (df["Stock Level"] >= 5) &
            (df["Price Gap"] <= 2000)
        ]
    return df

filtered_df = filter_by_category(df.copy(), category)

# --- UI: Apply / Revert ---
selected_ids = []

if category != "High Confidence":
    select_all = st.checkbox("✅ Select All", key="select_all_main")
    col_apply, col_revert = st.columns([1, 1])
    with col_apply:
        apply_clicked = st.button("🚀 Apply Selected")
    with col_revert:
        revert_clicked = st.button("↩️ Revert Selected")
else:
    # If hiding buttons, we still need to define these for logic below
    apply_clicked = False
    revert_clicked = False
    select_all = False  # Prevent preselecting checkboxes


# --- Product Cards ---
for _, row in filtered_df.iterrows():
    pid = row["ProductID"]
    is_applied = row["Applied"]
    needs_review = row["Confidence Score"] < 0.70 or row["Stock Level"] < 5 or row["Price Gap"] > 2000
    bg_color = "#dcfce7" if is_applied else ("#fff3cd" if needs_review else "#e0f7fa")

    with st.container():
        cols = st.columns([0.05, 0.95])
        if category != "High Confidence":
            checked = select_all or cols[0].checkbox("", key=f"chk_{pid}")
        else:
            checked = False
            cols[0].markdown("")  # leave the space empty

        if checked:
            selected_ids.append(pid)

        with cols[1]:
            st.markdown(f"""
                <div style='padding:10px; border:1px solid #ccc; border-radius:10px; background:{bg_color}; margin-bottom:10px;'>
                    <b>{row['ProductName']}</b> ({'<span style="color:green;">Applied</span>' if is_applied else 'Not Applied'})<br>
                    💰 Our Price: ₹{int(row['Our Price'])} → AI Price: ₹{int(row['AI Price'])}<br>
                    🎯 Confidence: {row['Confidence Score']*100:.0f}% {'✅' if row['Confidence Score'] >= 0.70 else '⚠️'} 
                    💸 Price Gap: ₹{int(row['Price Gap'])} {'⚠️' if row['Price Gap'] > 2000 else ''} 
                    📦 Stock: {int(row['Stock Level'])} {'🔻' if row['Stock Level'] < 5 else ''}
                </div>
            """, unsafe_allow_html=True)

# --- Apply Selected ---
if apply_clicked:
    for pid in selected_ids:
        row = df[df["ProductID"] == pid].iloc[0]
        ai_overrides = [o for o in ai_overrides if o.get("product_id") != pid]
        ai_overrides.append({
            "product_id": pid,
            "product_name": row["ProductName"],
            "ai_price": float(row["AI Price"]),
            "confidence": float(row["Confidence Score"]),
            "OverrideType": "AI Recommended"
        })
    with open(AI_JSON_PATH, "w") as f:
        json.dump(ai_overrides, f, indent=2)
    st.success("✅ Selected AI Recommendations Applied.")
    st.rerun()

# --- Revert Selected ---
if revert_clicked:
    ai_overrides = [o for o in ai_overrides if o.get("product_id") not in selected_ids]
    with open(AI_JSON_PATH, "w") as f:
        json.dump(ai_overrides, f, indent=2)
    st.warning("↩️ Selected AI Recommendations Reverted.")
    st.rerun()
