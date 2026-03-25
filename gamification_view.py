import streamlit as st


def gamification_section(summary):
    st.markdown("### 🎮 Training Consistency")
    c1, c2 = st.columns(2)
    c1.metric("Current Flight Streak", f"{summary.current_streak_days} days")
    c2.metric("Longest Flight Streak", f"{summary.longest_streak_days} days")