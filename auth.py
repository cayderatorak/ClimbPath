import streamlit as st

def authenticate_user(email, password):
    if email and password:
        return {
            "id": email,  # temporary ID
            "email": email,
            "name": email.split("@")[0]
        }
    return None

def login():

    st.markdown(
        """
        <h1 style='text-align: center;'>✈️ ClimbPath</h1>
        <p style='text-align: center; font-size:18px;'>
        Track your journey from first lesson to checkride
        </p>
        """,
        unsafe_allow_html=True
    )

    st.markdown("---")

    # Role selection buttons
    col1, col2 = st.columns(2)

    if col1.button("🧑‍🎓 Student", use_container_width=True):
        st.session_state.role = "student"

    if col2.button("🧑‍✈️ Instructor", use_container_width=True):
        st.session_state.role = "instructor"

    st.markdown("---")

    if "role" in st.session_state:

        st.subheader(f"{st.session_state.role.capitalize()} Login")

        email = st.text_input("Email")
        password = st.text_input("Password", type="password")

        if st.button("Login", use_container_width=True):

            user = authenticate_user(email, password)

            if user:
                user["role"] = st.session_state.role
                return user
            else:
                st.error("Invalid email or password")

    return None