import streamlit as st
from database import supabase
from datetime import datetime

def login():
    if "user" not in st.session_state:
        st.session_state.user = None

    if st.session_state.user:
        return st.session_state.user

    st.title("✈️ ClimbPath Login")
    email = st.text_input("Email")
    password = st.text_input("Password", type="password")
    col1, col2 = st.columns(2)

    with col1:
        if st.button("Login"):
            try:
                resp = supabase.auth.sign_in_with_password({"email": email, "password": password})
                st.session_state.user = resp.user
                st.rerun()
            except:
                st.error("Invalid login")

    with col2:
        if st.button("Signup"):
            try:
                supabase.auth.sign_up({"email": email, "password": password})
                st.success("Account created!")
            except:
                st.error("Signup failed")

    st.stop()