import streamlit as st


def gamification_section(summary):
    st.markdown("### 🎮 Training Momentum")
    c1, c2, c3 = st.columns(3)
    c1.metric("XP", summary.total_xp)
    c2.metric("Level", summary.level)
    c3.metric("Current Streak", f"{summary.current_streak_days} days")

    progress_to_next = 0
    if summary.next_level_xp > 0:
        progress_to_next = min(summary.total_xp / summary.next_level_xp, 1.0)

    st.progress(progress_to_next, text=f"Progress to next level: {summary.total_xp}/{summary.next_level_xp} XP")
    st.caption(f"Longest streak: {summary.longest_streak_days} days")
