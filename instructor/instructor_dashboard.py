import streamlit as st
from database import supabase

def show(user):

    st.title("🧑‍✈️ Instructor Dashboard")

    students = (
        supabase
        .table("students")
        .select("*")
        .eq("instructor_id", user["id"])
        .execute()
    )

    students = students.data

    st.subheader("Your Students")

    for s in students:

        col1,col2,col3,col4 = st.columns([3,1,2,1])

        col1.write(s["name"])
        col2.write(f'{s["hours"]} hrs')
        col3.write(s["stage"])

        if col4.button("Open", key=s["id"]):
            st.session_state.selected_student = s["id"]


email = st.text_input("Student Email")

if st.button("Send Invite"):

    invite = {
        "email": email,
        "instructor_id": user["id"]
    }

    supabase.table("invites").insert(invite).execute()

    st.success("Invite sent!")