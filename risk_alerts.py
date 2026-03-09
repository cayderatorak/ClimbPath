import streamlit as st

def risk_section(risk_alerts):
    st.markdown("### ⚠️ Training Risk Alerts")
    if risk_alerts:
        for risk in risk_alerts:
            st.warning(risk)
    else:
        st.success("No training risks detected")