import streamlit as st
from datetime import datetime, timedelta
from utils.data_loader import load_product_data
from utils.overrides import save_override
from utils.override_handler import load_scheduled_overrides, save_scheduled_overrides

st.title("🛠️ Manual Price Override")

df = load_product_data()

# Step 1: Product Selection
product = st.selectbox("Select a product to override pricing", df["ProductName"])
selected = df[df["ProductName"] == product].iloc[0]

# Step 2: Show current price
st.markdown(f"**Current Price:** ₹{selected['Our Price']}")

# Step 3: Input new price
new_price = st.number_input("Enter new price", min_value=0, value=int(selected["Our Price"]))

# Step 4: Reason selection
reason = st.selectbox("Reason for override", [
    "Brand positioning",
    "Inventory concerns",
    "Promotional strategy",
    "Other"
])

custom_reason = ""
if reason == "Other":
    custom_reason = st.text_area("Enter custom reason")

# Step 5: Expiry input
expire_date = st.date_input("📅 Expire On Date", value=datetime.now().date())
expire_time = st.time_input("⏳ Expire Time", value=(datetime.now() + timedelta(hours=4)).time())
expires_on = datetime.combine(expire_date, expire_time)

# Submit
if st.button("Submit Override"):
    final_reason = reason if reason != "Other" else custom_reason
    if not final_reason.strip():
        st.warning("⚠️ Please enter a reason for override.")
    else:
        # Save override (immediate effect)
        save_override(product, new_price, final_reason, expires_on.strftime("%Y-%m-%d %H:%M:%S"))
        st.success(f"✅ Override applied immediately for *{product}*.")
        st.markdown(f"""
        - **Old Price:** ₹{selected['Our Price']}
        - **New Price:** ₹{new_price}
        - **Reason:** {final_reason}
        - **Expires On:** {expires_on.strftime('%Y-%m-%d %H:%M:%S')}
        """)

# -------------------------
# Manage existing overrides
# -------------------------
st.title("🗑️ Manage Scheduled Overrides")

overrides = load_scheduled_overrides()

if not overrides:
    st.info("No overrides scheduled.")
else:
    for i, item in enumerate(overrides):
        # Robust handling of scheduled_for vs expires_on
        scheduled = item.get("scheduled_for")
        expires = item.get("expires_on")
        time_info = f"at {scheduled}" if scheduled else (f"until {expires}" if expires else "⏳ unknown time")

        with st.expander(f"{item['product']} → ₹{item['new_price']} {time_info}"):
            st.write(f"📌 Reason: {item['reason']}")
            if st.button(f"❌ Delete Override {i+1}", key=f"delete_{i}"):
                overrides.pop(i)
                save_scheduled_overrides(overrides)
                st.success("✅ Override deleted.")
                st.rerun()
