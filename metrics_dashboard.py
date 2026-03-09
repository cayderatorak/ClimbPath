import streamlit as st

def dashboard_metrics(totals, milestone, solo_score, predicted_solo, solo_confidence, total_spent, remaining_cost):
    c1,c2,c3,c4,c5,c6 = st.columns(6)
    c1.metric("Total Hours", round(totals["Total"],1))
    c2.metric("Next Milestone", milestone)
    c3.metric("Solo Readiness", f"{solo_score}%")
    c4.metric("Predicted Solo", predicted_solo.strftime("%Y-%m-%d"), f"{solo_confidence}% confidence")
    c5.metric("Total Spent", f"${total_spent:,.0f}")
    c6.metric("Remaining Cost", f"${remaining_cost:,.0f}")