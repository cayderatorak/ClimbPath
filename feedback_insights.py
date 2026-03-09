import streamlit as st

def feedback_section(feedback_insights):
    st.markdown("### 🧠 Instructor Feedback Insights")
    if feedback_insights:
        sorted_items = sorted(feedback_insights.items(), key=lambda x: x[1], reverse=True)
        for category, count in sorted_items:
            if count >= 5:
                label = "Focus Area ⚠️"
            elif count >= 2:
                label = "Improving 👍"
            else:
                label = "Mentioned"
            st.write(f"**{category}** — {label} ({count} mentions)")
    else:
        st.write("No instructor feedback available yet.")