import streamlit as st
from background import auto_data_scheduler

st.title("📦 Mock Data Generator")

if auto_data_scheduler.is_running():
    st.success("Auto generation is running.")
else:
    st.warning("Auto generation is stopped.")

interval = st.number_input("Set interval (minutes)", min_value=1, max_value=60, value=5)

col1, col2, col3 = st.columns(3)

with col1:
    if st.button("▶️ Start Auto Generation"):
        auto_data_scheduler.start_auto_generation(interval)
        st.success("Started auto data generation.")

with col2:
    if st.button("⏹ Stop Auto Generation"):
        auto_data_scheduler.stop_auto_generation()
        st.info("Stopped auto data generation.")

with col3:
    if st.button("⚡ Generate Once"):
        auto_data_scheduler.generate_and_save_data()
        st.success("Mock data generated once.")

st.markdown("---")
st.subheader("📄 Log Output")

with open("data/mock_data_generation_log.txt", "r") as f:
    logs = f.read().splitlines()[-10:]
    for log in reversed(logs):
        st.text(log)
