import streamlit as st

def faa_progress(totals, track):
    st.markdown("### FAA Progress")
    for cat in ["Dual","Solo","XC","Night"]:
        percent = min(totals.get(cat,0)/track[cat]*100,100)
        st.write(f"{cat}: {totals.get(cat,0):.1f}/{track[cat]}")
        st.progress(percent/100)