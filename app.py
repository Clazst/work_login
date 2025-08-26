
import streamlit as st
import pandas as pd
from datetime import datetime, time

# Title of the app
st.title("🕒 Work Hours Logger & Leave Calculator")

# Initialize session state for work log
if "work_log" not in st.session_state:
    st.session_state.work_log = pd.DataFrame(columns=["Date", "Start Time", "End Time", "Hours Worked"])

# Function to calculate hours worked
def calculate_hours(start, end):
    return (datetime.combine(datetime.today(), end) - datetime.combine(datetime.today(), start)).seconds / 3600

# Preloaded entries
preloaded_entries = [
    {"Date": "Saturday", "Start Time": time(8, 0), "End Time": time(20, 0)},
    {"Date": "Sunday", "Start Time": time(8, 0), "End Time": time(20, 0)},
    {"Date": "Monday", "Start Time": time(8, 0), "End Time": time(18, 0)},
]

# Load preloaded entries only once
if "preloaded" not in st.session_state:
    for entry in preloaded_entries:
        hours = calculate_hours(entry["Start Time"], entry["End Time"])
        st.session_state.work_log.loc[len(st.session_state.work_log)] = [entry["Date"], entry["Start Time"], entry["End Time"], hours]
    st.session_state.preloaded = True

# Input form for new entries
with st.form("log_form"):
    st.subheader("Log New Work Entry")
    date = st.text_input("Day (e.g., Tuesday)")
    start_time = st.time_input("Start Time", time(9, 0))
    end_time = st.time_input("End Time", time(17, 0))
    submitted = st.form_submit_button("Add Entry")

    if submitted:
        hours = calculate_hours(start_time, end_time)
        st.session_state.work_log.loc[len(st.session_state.work_log)] = [date, start_time, end_time, hours]
        st.success(f"Logged {hours:.2f} hours for {date}")

# Display work log
st.subheader("📋 Work Log Summary")
st.dataframe(st.session_state.work_log)

# Total hours and leave calculation
total_hours = st.session_state.work_log["Hours Worked"].sum()
leave_hours = total_hours // 8  # 1 hour leave per 8 hours worked

st.subheader("📊 Summary")
st.write(f"**Total Hours Worked:** {total_hours:.2f}")
st.write(f"**Leave Earned:** {leave_hours:.0f} hours")

# Instructions for deployment
st.markdown("---")
st.markdown("✅ Ready to deploy on [Streamlit Cloud](https://streamlit.io/cloud). Upload this `app.py` to a GitHub repo and connect it to Streamlit Cloud to go live!")
