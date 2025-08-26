
import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime

# Initialize session state
if 'log' not in st.session_state:
    st.session_state.log = []

if 'university_leave' not in st.session_state:
    st.session_state.university_leave = 14.0  # Starting university leave

if 'bookdash_leave' not in st.session_state:
    st.session_state.bookdash_leave = 0.0  # Starting BookDash overtime leave

# Title
st.title("Work Hours Logger & Leave Tracker")

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
        hours_worked = (end_dt - start_dt).total_seconds() / 3600

        # Determine day of week
        day_of_week = date.strftime("%A")

        # Calculate leave earned
        leave_earned = 0.0
        university_leave_used = 0.0
        bookdash_leave_earned = 0.0

        if day_of_week == "Saturday":
            bookdash_leave_earned = 1.5
            st.session_state.bookdash_leave += bookdash_leave_earned
        elif day_of_week == "Sunday":
            bookdash_leave_earned = 2.0
            st.session_state.bookdash_leave += bookdash_leave_earned
        else:
            leave_earned = hours_worked / 8.0
            university_leave_used = leave_earned
            st.session_state.university_leave -= university_leave_used

        # Log entry
        st.session_state.log.append({
            "Date": date,
            "Day": day_of_week,
            "Start": start_time.strftime("%H:%M"),
            "End": end_time.strftime("%H:%M"),
            "Hours Worked": round(hours_worked, 2),
            "University Leave Used": round(university_leave_used, 2),
            "BookDash Leave Earned": round(bookdash_leave_earned, 2)
        })

# Display log
if st.session_state.log:
    df = pd.DataFrame(st.session_state.log)
    st.subheader("Work Log")
    st.dataframe(df)

    # Summary
    total_hours = df["Hours Worked"].sum()
    total_university_leave_used = df["University Leave Used"].sum()
    total_bookdash_leave_earned = df["BookDash Leave Earned"].sum()

    st.markdown(f"**Total Hours Worked:** {total_hours:.2f}")
    st.markdown(f"**University Leave Remaining:** {st.session_state.university_leave:.2f} days")
    st.markdown(f"**BookDash Leave Earned:** {st.session_state.bookdash_leave:.2f} days")

    # Charts
    st.subheader("Visual Dashboard")

    # Hours worked per day
    fig_hours = px.bar(df, x="Date", y="Hours Worked", color="Day", title="Hours Worked Per Day")
    st.plotly_chart(fig_hours)

    # Leave earned over time
    df_leave = df.copy()
    df_leave["Total Leave Earned"] = df_leave["BookDash Leave Earned"] + df_leave["University Leave Used"]
    fig_leave = px.line(df_leave, x="Date", y="Total Leave Earned", title="Leave Earned Over Time")
    st.plotly_chart(fig_leave)
