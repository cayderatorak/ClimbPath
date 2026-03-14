import streamlit as st

def _label_for_mentions(count: int) -> str:
    if count >= 5:
        return "Priority Focus ⚠️"
    if count >= 2:
        return "Improving 👍"
    return "Mentioned"

def feedback_section(feedback_insights):
    st.markdown("### 🧠 Instructor Feedback Insights")
    if not feedback_insights:
        st.write("No instructor feedback available yet.")
        return

    summary = feedback_insights.get("summary")
    categories = feedback_insights.get("categories", {})
    legacy_counts = feedback_insights.get("legacy_counts", {})
    actions = feedback_insights.get("actions", [])
    sentiment = feedback_insights.get("sentiment", {})

    if summary:
        st.info(summary)

    # Backward compatibility for old dict format if needed.
    if not categories and legacy_counts:
        categories = {k: {"mentions": v, "sample_notes": []} for k, v in legacy_counts.items()}

    if categories:
        sorted_items = sorted(categories.items(), key=lambda item: item[1].get("mentions", 0), reverse=True)
        for category, data in sorted_items:
            mentions = int(data.get("mentions", 0))
            label = _label_for_mentions(mentions)
            st.write(f"**{category}** — {label} ({mentions} mentions)")
            for sample in data.get("sample_notes", [])[:1]:
                st.caption(f"Example: {sample}")

    if actions:
        st.markdown("#### Recommended next steps")
        for idx, action in enumerate(actions, 1):
            st.write(f"{idx}. {action}")

    trend = sentiment.get("trend")
    if trend:
        st.caption(f"Feedback trend: **{trend}**")