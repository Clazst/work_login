import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime, date
from io import BytesIO
from fpdf import FPDF
import os

# Constants
EXCEL_FILE = "work_log.xlsx"
INITIAL_LEAVE_BALANCE = 14.0

# Load existing data or initialize
if os.path.exists(EXCEL_FILE):
    df = pd.read_excel(EXCEL_FILE, engine='openpyxl')
else:
    df = pd.DataFrame(columns=["Date", "Start Time", "End Time", "Hours Worked", "Leave Type", "Leave Earned"])

# Sidebar filters
st.sidebar.header("Filters")
selected_year = st.sidebar.selectbox("Select Year", sorted(df['Date'].dt.year.unique()) if not df.empty else [date.today().year])
selected_month = st.sidebar.selectbox("Select Month", list(range(1, 13)))
selected_leave_type = st.sidebar.selectbox("Select Leave Type", ["All", "University", "BookDash"])

# Title
st.title("Work Hours Logger and Leave Dashboard")

# Log new work
st.subheader("Log Work Hours")
with st.form("log_form"):
    work_date = st.date_input("Date", date.today())
    start_time = st.time_input("Start Time")
    end_time = st.time_input("End Time")
    submitted = st.form_submit_button("Log Work")

    if submitted:
        start_dt = datetime.combine(work_date, start_time)
        end_dt = datetime.combine(work_date, end_time)
        hours_worked = (end_dt - start_dt).seconds / 3600

        weekday = work_date.weekday()
        if weekday == 5:  # Saturday
            leave_earned = 1.5
            leave_type = "BookDash"
        elif weekday == 6:  # Sunday
            leave_earned = 2.0
            leave_type = "BookDash"
        else:
            leave_earned = hours_worked / 8
            leave_type = "University"

        new_entry = {
            "Date": work_date,
            "Start Time": start_time.strftime("%H:%M"),
            "End Time": end_time.strftime("%H:%M"),
            "Hours Worked": hours_worked,
            "Leave Type": leave_type,
            "Leave Earned": round(leave_earned, 2)
        }

        df = pd.concat([df, pd.DataFrame([new_entry])], ignore_index=True)
        df.to_excel(EXCEL_FILE, index=False, engine='openpyxl')
        st.success("Work logged successfully!")

# Filtered data
df['Date'] = pd.to_datetime(df['Date'])
filtered_df = df[
    (df['Date'].dt.year == selected_year) &
    (df['Date'].dt.month == selected_month)
]
if selected_leave_type != "All":
    filtered_df = filtered_df[filtered_df['Leave Type'] == selected_leave_type]

# Dashboard
st.subheader("Dashboard")
if not filtered_df.empty:
    total_hours = filtered_df["Hours Worked"].sum()
    university_leave_used = df[df["Leave Type"] == "University"]["Leave Earned"].sum()
    bookdash_leave_earned = df[df["Leave Type"] == "BookDash"]["Leave Earned"].sum()
    university_leave_remaining = max(0, INITIAL_LEAVE_BALANCE - university_leave_used)

    col1, col2, col3 = st.columns(3)
    col1.metric("Total Hours Worked", f"{total_hours:.2f}")
    col2.metric("University Leave Remaining", f"{university_leave_remaining:.2f} days")
    col3.metric("BookDash Leave Earned", f"{bookdash_leave_earned:.2f} days")

    # Chart
    fig = px.bar(filtered_df, x="Date", y="Hours Worked", color="Leave Type", title="Hours Worked by Date")
    st.plotly_chart(fig, use_container_width=True)

    # Table
    st.dataframe(filtered_df)

    # Export to Excel
    excel_buffer = BytesIO()
    with pd.ExcelWriter(excel_buffer, engine='openpyxl') as writer:
        filtered_df.to_excel(writer, index=False)
    st.download_button("Download Excel", data=excel_buffer.getvalue(), file_name="work_log_filtered.xlsx")

    # Export to PDF
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, txt="Work Log Summary", ln=True, align='C')
    pdf.ln(10)

    for index, row in filtered_df.iterrows():
        line = f"{row['Date'].date()} | {row['Start Time']} - {row['End Time']} | {row['Hours Worked']} hrs | {row['Leave Type']} | {row['Leave Earned']} days"
        pdf.cell(200, 10, txt=line, ln=True)

    pdf_bytes = pdf.output(dest='S').encode('latin1')
    pdf_buffer = BytesIO(pdf_bytes)
    st.download_button("Download PDF", data=pdf_buffer.getvalue(), file_name="work_log_filtered.pdf")
else:
    st.info("No data available for the selected filters.")

