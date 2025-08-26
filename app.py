import streamlit as st
import pandas as pd
import plotly.express as px
from fpdf import FPDF
from io import BytesIO
from datetime import datetime

# Initialize session state
if 'work_log' not in st.session_state:
    st.session_state.work_log = pd.DataFrame(columns=['Date', 'Start Time', 'End Time', 'Hours Worked', 'Day', 'Leave Type', 'Leave Earned'])

# Title
st.title("📊 Work Hours Logger & Leave Dashboard")

# Sidebar filters
st.sidebar.header("🔍 Filters")
selected_year = st.sidebar.selectbox("Year", options=sorted(set(pd.to_datetime(st.session_state.work_log['Date']).dt.year), reverse=True) if not st.session_state.work_log.empty else [datetime.now().year])
selected_month = st.sidebar.selectbox("Month", options=list(range(1, 13)))
selected_leave_type = st.sidebar.selectbox("Leave Type", options=["All", "University", "BookDash"])

# Log work section
st.subheader("🕒 Log Work Hours")
with st.form("log_work_form"):
    date = st.date_input("Date")
    start_time = st.time_input("Start Time")
    end_time = st.time_input("End Time")
    submitted = st.form_submit_button("Log Work")
    if submitted:
        hours_worked = (datetime.combine(date, end_time) - datetime.combine(date, start_time)).seconds / 3600
        day_name = date.strftime("%A")
        if day_name == "Saturday":
            leave_type = "BookDash"
            leave_earned = 1.5
        elif day_name == "Sunday":
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
            'Day': day_name,
            'Leave Type': leave_type,
            'Leave Earned': round(leave_earned, 2)
        }
        st.session_state.work_log = pd.concat([st.session_state.work_log, pd.DataFrame([new_entry])], ignore_index=True)
        st.success("Work logged successfully!")

# Filtered data
filtered_data = st.session_state.work_log.copy()
filtered_data['Date'] = pd.to_datetime(filtered_data['Date'])
filtered_data = filtered_data[filtered_data['Date'].dt.year == selected_year]
filtered_data = filtered_data[filtered_data['Date'].dt.month == selected_month]
if selected_leave_type != "All":
    filtered_data = filtered_data[filtered_data['Leave Type'] == selected_leave_type]

# Dashboard
st.subheader("📈 Dashboard")
if not filtered_data.empty:
    total_hours = filtered_data['Hours Worked'].sum()
    university_leave = filtered_data[filtered_data['Leave Type'] == 'University']['Leave Earned'].sum()
    bookdash_leave = filtered_data[filtered_data['Leave Type'] == 'BookDash']['Leave Earned'].sum()
    st.metric("Total Hours Worked", f"{total_hours:.2f}")
    st.metric("University Leave Earned", f"{university_leave:.2f} days")
    st.metric("BookDash Leave Earned", f"{bookdash_leave:.2f} days")

    fig = px.bar(filtered_data, x='Date', y='Hours Worked', color='Leave Type',
                 title="Hours Worked by Date", color_discrete_map={'University': 'royalblue', 'BookDash': 'orange'})
    st.plotly_chart(fig, use_container_width=True)

    fig2 = px.pie(filtered_data, names='Leave Type', values='Leave Earned',
                  title="Leave Distribution", color_discrete_map={'University': 'royalblue', 'BookDash': 'orange'})
    st.plotly_chart(fig2, use_container_width=True)

    st.dataframe(filtered_data)

    # Export to Excel
    def to_excel(df):
        output = BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, index=False, sheet_name='Work Log')
        return output.getvalue()

    st.download_button("📥 Download Excel", data=to_excel(filtered_data),
                       file_name="work_log.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

    # Export to PDF
    def to_pdf(df):
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", size=12)
        pdf.cell(200, 10, txt="Work Log Report", ln=True, align='C')
        for index, row in df.iterrows():
            line = f"{row['Date']} | {row['Start Time']}-{row['End Time']} | {row['Hours Worked']} hrs | {row['Leave Type']} | {row['Leave Earned']} days"
            pdf.cell(200, 10, txt=line, ln=True)
        return pdf.output(dest='S').encode('latin1')

    st.download_button("📥 Download PDF", data=to_pdf(filtered_data),
                       file_name="work_log.pdf", mime="application/pdf")
else:
    st.info("No data available for the selected filters.")

