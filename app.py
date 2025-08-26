
import streamlit as st
import pandas as pd
from datetime import datetime

# Initialize session state for work log and leave balance
if 'work_log' not in st.session_state:
    st.session_state.work_log = []

if 'leave_balance' not in st.session_state:
    st.session_state.leave_balance = 14.0  # Starting leave balance in days

# Title
st.title("Work Hours Logger and Leave Tracker")

# Input form
with st.form("log_form"):
    date = st.date_input("Date")
    start_time = st.time_input("Start Time")
    end_time = st.time_input("End Time")
    submitted = st.form_submit_button("Log Work")

    if submitted:
        # Calculate hours worked
        start_dt = datetime.combine(date, start_time)
        end_dt = datetime.combine(date, end_time)
        hours_worked = (end_dt - start_dt).seconds / 3600

        # Determine leave earned
        weekday = date.strftime('%A')
        if weekday == 'Saturday':
            leave_earned = 1.5
        elif weekday == 'Sunday':
            leave_earned = 2.0
        else:
            leave_earned = hours_worked / 8.0

        # Update leave balance
        st.session_state.leave_balance += leave_earned

        # Append to work log
        st.session_state.work_log.append({
            'Date': date.strftime('%Y-%m-%d'),
            'Day': weekday,
            'Start': start_time.strftime('%H:%M'),
            'End': end_time.strftime('%H:%M'),
            'Hours Worked': hours_worked,
            'Leave Earned': leave_earned
        })

# Display work log
if st.session_state.work_log:
    df = pd.DataFrame(st.session_state.work_log)
    st.subheader("Work Log")
    st.dataframe(df)

    total_hours = df['Hours Worked'].sum()
    total_leave = df['Leave Earned'].sum()

    st.markdown(f"**Total Hours Worked:** {total_hours:.2f}")
    st.markdown(f"**Total Leave Earned:** {total_leave:.2f} days")
    st.markdown(f"**Current Leave Balance:** {st.session_state.leave_balance:.2f} days")
else:
    st.info("No work hours logged yet.")
