import streamlit as st

def school_comparison(totals, school_avg):
    st.markdown("### Progress vs School Averages")
    if school_avg:
        for key,val in school_avg.items():
            st.write(f"{key}: You {totals.get(key,0)} hrs • School Avg {val:.1f} hrs")