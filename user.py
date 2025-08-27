import streamlit as st
import pandas as pd
import datetime
import os

# File to store user data
DATA_FILE = "user_data.xlsx"

# Load existing data or create new DataFrame
if os.path.exists(DATA_FILE):
    df = pd.read_excel(DATA_FILE, engine='openpyxl')
else:
    df = pd.DataFrame(columns=[
        "Username", "Company", "Part-time Work", "Date", "Start Time", "End Time",
        "Hours Worked", "Leave Used", "Leave Type"
    ])

# Sidebar for user login
st.sidebar.title("User Login")
username = st.sidebar.text_input("Enter your username")
company = st.sidebar.text_input("Company Name")
part_time = st.sidebar.text_input("Part-time Work Description")

if username:
    st.title(f"Welcome, {username} 👋")
    st.subheader("Master Work Hours & Leave Dashboard")

    # Work log entry
    st.markdown("### Log Work Hours")
    date = st.date_input("Date", value=datetime.date.today())
    start_time = st.time_input("Start Time", value=datetime.time(9, 0))
    end_time = st.time_input("End Time", value=datetime.time(17, 0))
    leave_used = st.number_input("Leave Used (days)", min_value=0.0, step=0.5)
    leave_type = st.selectbox("Leave Type", ["University", "BookDash", "Other"])

    if st.button("Log Work"):
        hours_worked = (datetime.datetime.combine(date, end_time) - datetime.datetime.combine(date, start_time)).seconds / 3600
        new_entry = {
            "Username": username,
            "Company": company,
            "Part-time Work": part_time,
            "Date": date,
            "Start Time": start_time,
            "End Time": end_time,
            "Hours Worked": hours_worked,
            "Leave Used": leave_used,
            "Leave Type": leave_type
        }
        df = pd.concat([df, pd.DataFrame([new_entry])], ignore_index=True)
        df.to_excel(DATA_FILE, index=False, engine='openpyxl')
        st.success("Work log saved successfully!")

    # Display dashboard
    st.markdown("### Dashboard")
    user_df = df[df["Username"] == username]
    st.dataframe(user_df)

    # Summary
    total_hours = user_df["Hours Worked"].sum()
    total_leave = user_df["Leave Used"].sum()
    st.metric("Total Hours Worked", f"{total_hours:.2f} hrs")
    st.metric("Total Leave Used", f"{total_leave:.2f} days")

    # Leave type breakdown
    leave_summary = user_df.groupby("Leave Type")["Leave Used"].sum().reset_index()
    st.markdown("#### Leave Type Summary")
    st.dataframe(leave_summary)
else:
    st.warning("Please enter your username to access the dashboard.")

