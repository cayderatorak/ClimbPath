import streamlit as st

def show(student):

    st.title(student["name"])

    col1,col2,col3 = st.columns(3)

    col1.metric("Hours", student["hours"])
    col2.metric("Solo Readiness", f'{student["solo_score"]}%')
    col3.metric("Checkride ETA", student["checkride_eta"])

    st.subheader("Instructor Notes")

    note = st.text_area("Add Lesson Notes")

    if st.button("Save"):
        save_note(student["id"], note)