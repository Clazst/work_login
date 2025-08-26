import streamlit as st
import pandas as pd
from io import BytesIO
from fpdf import FPDF
import plotly.express as px

# Initialize session state
if 'work_log' not in st.session_state:
    st.session_state.work_log = []

if 'university_leave_balance' not in st.session_state:
    st.session_state.university_leave_balance = 14.0

if 'bookdash_leave_balance' not in st.session_state:
    st.session_state.bookdash_leave_balance = 0.0

st.title("Work Hours Logger and Leave Tracker")

# Input form
with st.form("log_form"):
    date = st.date_input("Date")
    start_time = st.time_input("Start Time")
    end_time = st.time_input("End Time")
    submitted = st.form_submit_button("Log Work")

    if submitted:
        hours_worked = (pd.Timestamp.combine(pd.Timestamp.today(), end_time) - 
                        pd.Timestamp.combine(pd.Timestamp.today(), start_time)).seconds / 3600
        day_name = date.strftime("%A")

        if day_name == "Saturday":
            leave_earned = 1.5
            leave_type = "BookDash"
            st.session_state.bookdash_leave_balance += leave_earned
        elif day_name == "Sunday":
            leave_earned = 2.0
            leave_type = "BookDash"
            st.session_state.bookdash_leave_balance += leave_earned
        else:
            leave_earned = round(hours_worked / 8, 2)
            leave_type = "University"
            st.session_state.university_leave_balance += leave_earned

        st.session_state.work_log.append({
            "Date": date.strftime("%Y-%m-%d"),
            "Day": day_name,
            "Start Time": start_time.strftime("%H:%M"),
            "End Time": end_time.strftime("%H:%M"),
            "Hours Worked": hours_worked,
            "Leave Type": leave_type,
            "Leave Earned": leave_earned
        })

# Display work log
df = pd.DataFrame(st.session_state.work_log)
if not df.empty:
    st.subheader("Work Log")
    st.dataframe(df)

    # Summary
    st.subheader("Leave Summary")
    st.write(f"University Leave Balance: {st.session_state.university_leave_balance:.2f} days")
    st.write(f"BookDash Leave Balance: {st.session_state.bookdash_leave_balance:.2f} days")

    # Charts
    fig = px.bar(df, x="Date", y="Hours Worked", color="Leave Type", title="Hours Worked by Date")
    st.plotly_chart(fig)

    # Export to Excel
    def to_excel(dataframe):
        output = BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            dataframe.to_excel(writer, index=False, sheet_name='Work Log')
        return output.getvalue()

    # Export to PDF
    def to_pdf(dataframe):
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", size=12)
        pdf.cell(200, 10, txt="Work Log Summary", ln=True, align='C')
        pdf.ln(10)

        col_width = pdf.w / (len(dataframe.columns) + 1)
        row_height = pdf.font_size + 2

        # Header
        for col in dataframe.columns:
            pdf.cell(col_width, row_height, col, border=1)
        pdf.ln(row_height)

        # Rows
        for _, row in dataframe.iterrows():
            for item in row:
                pdf.cell(col_width, row_height, str(item), border=1)
            pdf.ln(row_height)

        pdf_output = BytesIO()
        pdf_bytes = pdf.output(dest='S').encode('latin1')
        pdf_output.write(pdf_bytes)
        pdf_output.seek(0)
        return pdf_output.getvalue()

    excel_data = to_excel(df)
    pdf_data = to_pdf(df)

    st.download_button("📥 Download Excel", data=excel_data, file_name="work_log.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
    st.download_button("📥 Download PDF", data=pdf_data, file_name="work_log.pdf", mime="application/pdf")
