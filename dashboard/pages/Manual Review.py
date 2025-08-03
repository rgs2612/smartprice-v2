import os
import sys

# Dynamically add project root to path
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

import streamlit as st
from datetime import datetime, timedelta
from utils.data_loader import load_product_data
from utils.overrides import save_override
from utils.override_handler import load_scheduled_overrides, save_scheduled_overrides
from utils.helpers import filter_products_needing_attention

st.set_page_config(page_title="Manual Price Override", layout="wide")
st.title("🛠️ Manual Price Override")

# Load product data
df = load_product_data()

# 🔽 Alert Type Filter Dropdown (Low AI Confidence removed)
alert_filter = st.selectbox("Filter products by alert type", [
    "🧊 All Issues",
    "🔺 Price Gap Alert",
    "📦 Low Stock Alert"
])

# ⚙️ Filter Function (Low AI Confidence filter removed)
def get_alert_filtered_df(df, alert_type):
    if alert_type == "🔺 Price Gap Alert":
        return df[(abs(df["Our Price"] - df["Competitor Price"]) > 2000)]
    elif alert_type == "📦 Low Stock Alert":
        return df[df["Stock Level"] < 5]
    else:  # All Issues
        return filter_products_needing_attention(df)

# 🔍 Apply selected filter
filtered_df = get_alert_filtered_df(df, alert_filter)

if filtered_df.empty:
    st.success("✅ No products match the selected alert.")
    st.stop()

# Step 1: Product Selection (Filtered Only)
product = st.selectbox("Select a product to override pricing", filtered_df["ProductName"])
selected = filtered_df[filtered_df["ProductName"] == product].iloc[0]
product_id = selected["ProductID"]

# Step 2: Show current price
st.markdown(f"**Current Price:** ₹{selected['Our Price']}")

# Step 3: Input new price
new_price = st.number_input("Enter new price", min_value=0, value=int(selected["Our Price"]))

# Step 4: Reason selection
reason = st.selectbox("Reason for override", [
    "Brand positioning", "Inventory concerns", "Promotional strategy", "Other"
])
custom_reason = st.text_area("Enter custom reason") if reason == "Other" else ""
final_reason = custom_reason.strip() if reason == "Other" else reason

# Step 5: Schedule Start Time
start_date = st.date_input("🕒 Start Override On Date", value=datetime.now().date())
start_time_str = st.text_input("⏱️ Start Time (HH:MM)", value=datetime.now().strftime("%H:%M"))

# Step 6: Expiry input
expire_date = st.date_input("🗓️ Expire On Date", value=(datetime.now() + timedelta(days=1)).date())
expire_time_str = st.text_input("⏳ Expire Time (HH:MM)", value=(datetime.now() + timedelta(hours=4)).strftime("%H:%M"))

# Step 7: Parse times and Submit
try:
    start_time = datetime.strptime(start_time_str, "%H:%M").time()
    expire_time = datetime.strptime(expire_time_str, "%H:%M").time()
    scheduled_for = datetime.combine(start_date, start_time)
    expires_on = datetime.combine(expire_date, expire_time)

    if st.button("Submit Override"):
        if not final_reason:
            st.warning("⚠️ Please enter a reason for override.")
        else:
            overrides = load_scheduled_overrides()
            overrides.append({
                "product_id": product_id,
                "product_name": product,
                "new_price": new_price,
                "reason": final_reason,
                "scheduled_for": scheduled_for.strftime("%Y-%m-%d %H:%M:%S"),
                "expires_on": expires_on.strftime("%Y-%m-%d %H:%M:%S")
            })
            save_scheduled_overrides(overrides)
            st.success(f"✅ Override scheduled for *{product}*.")
            st.markdown(f"""
            - **Old Price:** ₹{selected['Our Price']}
            - **New Price:** ₹{new_price}
            - **Reason:** {final_reason}
            - **Scheduled For:** {scheduled_for.strftime('%Y-%m-%d %H:%M:%S')}
            - **Expires On:** {expires_on.strftime('%Y-%m-%d %H:%M:%S')}
            """)
except ValueError:
    st.error("❌ Please enter Start Time and Expire Time in HH:MM format.")

# -------------------------
# Manage existing overrides
# -------------------------
st.title("🗂️ Manage Scheduled Overrides")

overrides = load_scheduled_overrides()
if not overrides:
    st.info("No overrides scheduled.")
else:
    for i, item in reversed(list(enumerate(overrides))):
        product_name = item.get("product_name", "")
        price = item.get("new_price")
        reason = item.get("reason")
        scheduled = item.get("scheduled_for", "N/A")
        expires = item.get("expires_on", "N/A")

        with st.expander(f"{product_name} → ₹{price}"):
            st.write(f"📌 **Reason:** {reason}")
            st.write(f"🕒 **Scheduled For:** {scheduled}")
            st.write(f"⏳ **Expires On:** {expires}")
            if st.button(f"❌ Delete Override {i+1}", key=f"delete_{i}"):
                overrides.pop(i)
                save_scheduled_overrides(overrides)
                st.success("✅ Override deleted.")
                st.rerun()
