import streamlit as st

def ranking_section(rank, percentile, track_name):
    st.markdown("### Student Ranking")
    st.write(f"You are ranked #{rank} ({percentile} percentile) in {track_name}")