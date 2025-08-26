
import streamlit as st
import pandas as pd
from datetime import datetime, time

st.set_page_config(page_title="Work Hours Logger", layout="centered")

st.title("🕒 Work Hours Logger & Leave Tracker")

# Initialize session state
if "log" not in st.session_state:
    st.session_state.log = []
if "annual_leave" not in st.session_state:
    st.session_state.annual_leave = 14.0  # Starting leave balance

# Input form
with st.form("log_form"):
    date = st.date_input("Date")
    start_time = st.time_input("Start Time", value=time(8, 0))
    end_time = st.time_input("End Time", value=time(17, 0))
    submitted = st.form_submit_button("Log Work")

    if submitted:
        # Calculate hours worked
        start_dt = datetime.combine(date, start_time)
        end_dt = datetime.combine(date, end_time)
        hours_worked = (end_dt - start_dt).total_seconds() / 3600

        # Determine leave earned
        weekday = date.weekday()
        if weekday == 5:  # Saturday
            leave_earned = 1.5
        elif weekday == 6:  # Sunday
            leave_earned = 2.0
        else:
            leave_earned = hours_worked / 8.0

        # Update log and leave balance
        st.session_state.log.append({
            "Date": date.strftime("%Y-%m-%d"),
            "Day": date.strftime("%A"),
            "Start": start_time.strftime("%H:%M"),
            "End": end_time.strftime("%H:%M"),
            "Hours Worked": round(hours_worked, 2),
            "Leave Earned": round(leave_earned, 2)
        })
        st.session_state.annual_leave += leave_earned

# Display log
if st.session_state.log:
    st.subheader("📋 Work Log")
    df = pd.DataFrame(st.session_state.log)
    st.dataframe(df)

    total_hours = sum(entry["Hours Worked"] for entry in st.session_state.log)
    total_leave = sum(entry["Leave Earned"] for entry in st.session_state.log)

    st.markdown(f"**Total Hours Worked:** {total_hours:.2f}")
    st.markdown(f"**Total Leave Earned:** {total_leave:.2f}")
    st.markdown(f"**Annual Leave Balance:** {st.session_state.annual_leave:.2f} days")
else:
    st.info("No work hours logged yet.")
