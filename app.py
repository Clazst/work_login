import streamlit as st
import pandas as pd
import plotly.express as px
from fpdf import FPDF
from io import BytesIO
from datetime import datetime

# Initialize session state
if 'work_log' not in st.session_state:
    st.session_state.work_log = pd.DataFrame(columns=['Date', 'Start Time', 'End Time', 'Hours Worked', 'Leave Type', 'Leave Earned'])

# Title
st.title("Work Hours Logger & Leave Dashboard")

# Sidebar filters
st.sidebar.header("Filters")
selected_year = st.sidebar.selectbox("Select Year", options=sorted(set(pd.to_datetime(st.session_state.work_log['Date']).dt.year.tolist() + [datetime.now().year])))
selected_month = st.sidebar.selectbox("Select Month", options=list(range(1, 13)))
selected_leave_type = st.sidebar.selectbox("Select Leave Type", options=["All", "University", "BookDash"])

# Input form
with st.form("log_form"):
    date = st.date_input("Date")
    start_time = st.time_input("Start Time")
    end_time = st.time_input("End Time")
    submitted = st.form_submit_button("Log Work")

    if submitted:
        hours_worked = (datetime.combine(date, end_time) - datetime.combine(date, start_time)).seconds / 3600
        weekday = date.weekday()
        if weekday == 5:
            leave_type = "BookDash"
            leave_earned = 1.5
        elif weekday == 6:
            leave_type = "BookDash"
            leave_earned = 2.0
        else:
            leave_type = "University"
            leave_earned = hours_worked / 8

        new_entry = {
            'Date': date.strftime("%Y-%m-%d"),
            'Start Time': start_time.strftime("%H:%M"),
            'End Time': end_time.strftime("%H:%M"),
            'Hours Worked': round(hours_worked, 2),
            'Leave Type': leave_type,
            'Leave Earned': round(leave_earned, 2)
        }
        st.session_state.work_log = pd.concat([st.session_state.work_log, pd.DataFrame([new_entry])], ignore_index=True)

# Filtered data
filtered_data = st.session_state.work_log.copy()
filtered_data['Date'] = pd.to_datetime(filtered_data['Date'])
filtered_data = filtered_data[filtered_data['Date'].dt.year == selected_year]
filtered_data = filtered_data[filtered_data['Date'].dt.month == selected_month]
if selected_leave_type != "All":
    filtered_data = filtered_data[filtered_data['Leave Type'] == selected_leave_type]

# Display table
st.subheader("Logged Work Entries")
st.dataframe(filtered_data)

# Summary
total_hours = filtered_data['Hours Worked'].sum()
university_leave = filtered_data[filtered_data['Leave Type'] == 'University']['Leave Earned'].sum()
bookdash_leave = filtered_data[filtered_data['Leave Type'] == 'BookDash']['Leave Earned'].sum()

st.metric("Total Hours Worked", f"{total_hours:.2f}")
st.metric("University Leave Earned", f"{university_leave:.2f} days")
st.metric("BookDash Leave Earned", f"{bookdash_leave:.2f} days")

# Charts
if not filtered_data.empty:
    fig = px.bar(filtered_data, x='Date', y='Hours Worked', color='Leave Type',
                 title="Hours Worked by Date", color_discrete_map={'University': 'blue', 'BookDash': 'orange'})
    st.plotly_chart(fig)

    fig2 = px.pie(filtered_data, names='Leave Type', values='Leave Earned',
                  title="Leave Distribution", color_discrete_map={'University': 'blue', 'BookDash': 'orange'})
    st.plotly_chart(fig2)

# Export buttons
st.subheader("Export Work Log")

# Excel export
excel_buffer = BytesIO()
with pd.ExcelWriter(excel_buffer, engine='openpyxl') as writer:
    filtered_data.to_excel(writer, index=False, sheet_name='Work Log')
st.download_button("Download Excel", data=excel_buffer.getvalue(), file_name="work_log.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

# PDF export
pdf = FPDF()
pdf.add_page()
pdf.set_font("Arial", size=12)
pdf.cell(200, 10, txt="Work Log Summary", ln=True, align='C')
pdf.ln(10)

for index, row in filtered_data.iterrows():
    line = f"{row['Date'].strftime('%Y-%m-%d')} | {row['Start Time']} - {row['End Time']} | {row['Hours Worked']} hrs | {row['Leave Type']} | {row['Leave Earned']} days"
    pdf.cell(200, 10, txt=line, ln=True)

pdf_buffer = BytesIO(pdf.output(dest='S').encode('latin1'))
st.download_button("Download PDF", data=pdf_buffer.getvalue(), file_name="work_log.pdf", mime="application/pdf")

