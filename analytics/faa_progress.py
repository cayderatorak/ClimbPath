import streamlit as st
from pdf_reports import generate_training_report


def faa_progress(totals, track, student_name, total_hours, solo_hours, xc_hours):

    st.markdown("### FAA Progress")

    for cat in ["Dual", "Solo", "XC", "Night"]:
        percent = min(totals.get(cat, 0) / track[cat] * 100, 100)
        st.write(f"{cat}: {totals.get(cat,0):.1f}/{track[cat]}")
        st.progress(percent / 100)

    st.subheader("📄 Download Training Report")

    pdf_file = generate_training_report(
        student_name=student_name,
        total_hours=total_hours,
        solo_hours=solo_hours,
        xc_hours=xc_hours
    )

    st.download_button(
        label="✈️ Download My Training Report",
        data=pdf_file,
        file_name="climbpath_training_report.pdf",
        mime="application/pdf"
    )