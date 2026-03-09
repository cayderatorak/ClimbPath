import streamlit as st

def achievements_section(achievements_list):
    st.markdown("### Achievements")
    for badge in achievements_list:
        st.write("🏅",badge)