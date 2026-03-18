import streamlit as st

from checkride_trainer import build_checkride_session


def checkride_trainer_section(track_name, totals, feedback_insights):
    st.markdown("### 🤖 AI Checkride Trainer")
    session = build_checkride_session(track_name, totals, feedback_insights)

    st.metric("Readiness Estimate", f"{session['readiness_percent']}%")
    if session["focus_hint"]:
        st.info(session["focus_hint"])

    questions = session["questions"]
    if not questions:
        st.write("No checkride questions available yet for this track.")
        return

    if "checkride_q_index" not in st.session_state:
        st.session_state.checkride_q_index = 0

    idx = st.session_state.checkride_q_index % len(questions)
    question = questions[idx]

    st.write(f"**Category:** {question.category}")
    st.write(question.prompt)

    answer = st.text_area("Your answer", key=f"checkride_answer_{idx}")

    col1, col2 = st.columns(2)
    with col1:
        if st.button("Show coaching rubric"):
            st.markdown("**Strong answer should include:**")
            for point in question.good_answer_points:
                st.write(f"- {point}")
            if answer.strip():
                st.success("Great — compare your answer against the rubric and improve one point.")
            else:
                st.warning("Try answering first, then compare with the rubric.")

    with col2:
        if st.button("Next question"):
            st.session_state.checkride_q_index = (idx + 1) % len(questions)
            st.rerun()
