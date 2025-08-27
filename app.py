import streamlit as st
import pandas as pd
import plotly.express as px
from fpdf import FPDF
from io import BytesIO
from datetime import datetime

# Initialize session state for work log
if "work_log" not in st.session_state:
    st.session_state.work_log = pd.DataFrame(columns=["Date", "Start Time", "End Time", "Hours Worked", "Leave Type", "Leave Earned"])

# Sidebar filters
st.sidebar.header("Filters")
years = sorted(set(pd.to_datetime(st.session_state.work_log["Date"]).dt.year.tolist() + [datetime.now().year]))
selected_year = st.sidebar.selectbox("Year", options=years)
selected_month = st.sidebar.selectbox("Month", options=list(range(1, 13)))
selected_leave_type = st.sidebar.selectbox("Leave Type", options=["All", "University", "BookDash"])

# Work logging section
st.header("Log Work Hours")
date = st.date_input("Date")
start_time = st.time_input("Start Time")
end_time = st.time_input("End Time")

if st.button("Log Work"):
    hours_worked = (datetime.combine(datetime.today(), end_time) - datetime.combine(datetime.today(), start_time)).seconds / 3600
    weekday = date.weekday()
    if weekday == 5:  # Saturday
        leave_type = "BookDash"
        leave_earned = 1.5
    elif weekday == 6:  # Sunday
        leave_type = "BookDash"
        leave_earned = 2.0
    else:
        leave_type = "University"
        leave_earned = hours_worked / 8

    new_entry = {
        "Date": date.strftime("%Y-%m-%d"),
        "Start Time": start_time.strftime("%H:%M"),
        "End Time": end_time.strftime("%H:%M"),
        "Hours Worked": hours_worked,
        "Leave Type": leave_type,
        "Leave Earned": round(leave_earned, 2)
    }
    st.session_state.work_log = pd.concat([st.session_state.work_log, pd.DataFrame([new_entry])], ignore_index=True)
    st.success("Work logged successfully!")

# Filtered data
filtered_data = st.session_state.work_log.copy()
filtered_data["Date"] = pd.to_datetime(filtered_data["Date"])
filtered_data = filtered_data[
    (filtered_data["Date"].dt.year == selected_year) &
    (filtered_data["Date"].dt.month == selected_month)
]
if selected_leave_type != "All":
    filtered_data = filtered_data[filtered_data["Leave Type"] == selected_leave_type]

# Dashboard
st.header("Dashboard")
if not filtered_data.empty:
    total_hours = filtered_data["Hours Worked"].sum()
    total_leave = filtered_data["Leave Earned"].sum()

    col1, col2 = st.columns(2)
    col1.metric("Total Hours Worked", f"{total_hours:.2f}")
    col2.metric("Total Leave Earned", f"{total_leave:.2f}")

    fig = px.bar(filtered_data, x="Date", y="Hours Worked", color="Leave Type", title="Hours Worked per Day",
                 color_discrete_map={"University": "#636EFA", "BookDash": "#EF553B"})
    st.plotly_chart(fig)

    fig2 = px.pie(filtered_data, names="Leave Type", values="Leave Earned", title="Leave Distribution",
                  color_discrete_map={"University": "#00CC96", "BookDash": "#AB63FA"})
    st.plotly_chart(fig2)

    st.dataframe(filtered_data)

    # Export to Excel
    excel_buffer = BytesIO()
    with pd.ExcelWriter(excel_buffer, engine='openpyxl') as writer:
        filtered_data.to_excel(writer, index=False)
    st.download_button("Download Excel", data=excel_buffer.getvalue(), file_name="work_log.xlsx")

    # Export to PDF
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, txt="Work Log Summary", ln=True, align='C')
    for index, row in filtered_data.iterrows():
        pdf.cell(200, 10, txt=f"{row['Date'].strftime('%Y-%m-%d')} | {row['Start Time']} - {row['End Time']} | {row['Hours Worked']} hrs | {row['Leave Type']} | {row['Leave Earned']} days", ln=True)
    pdf_bytes = pdf.output(dest='S').encode('latin1')
    pdf_buffer = BytesIO(pdf_bytes)
    st.download_button("Download PDF", data=pdf_buffer.getvalue(), file_name="work_log.pdf")
else:
    st.info("No data available for the selected filters.")

