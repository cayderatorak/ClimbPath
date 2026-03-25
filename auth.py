import streamlit as st
from database import supabase


ROLE_OPTIONS = {
    "student": {"label": "🧑‍🎓 Student", "help": "Log in to track training, progress, and readiness."},
    "instructor": {"label": "🧑‍✈️ Instructor", "help": "Log in to review students and manage invites."},
}


def _normalize_user(auth_user, role):
    user_id = getattr(auth_user, "id", None) or getattr(auth_user, "email", None)
    email = getattr(auth_user, "email", "") or ""

    return {
        "id": user_id,
        "email": email,
        "name": email.split("@")[0] if email else "Pilot",
        "role": role,
    }


def authenticate_user(email, password, role):
    response = supabase.auth.sign_in_with_password({"email": email, "password": password})
    return _normalize_user(response.user, role)


def login():
    if "user" not in st.session_state:
        st.session_state.user = None

    if st.session_state.user is None:
        try:
            current_user = supabase.auth.get_user().user
            if current_user:
                selected_role = st.session_state.get("role", "student")
                st.session_state.user = _normalize_user(current_user, selected_role)
        except Exception:
            # No persisted auth session available yet (or token refresh failed).
            pass

    if st.session_state.user:
        return st.session_state.user

    st.markdown(
        """
        <h1 style='text-align: center;'>✈️ My ClimbPath</h1>
        <p style='text-align: center; font-size:18px;'>
        Track your journey from first lesson to checkride
        </p>
        """,
        unsafe_allow_html=True
    )

    st.markdown("---")

    selected_role = st.radio(
        "Choose how you want to sign in",
        options=list(ROLE_OPTIONS.keys()),
        format_func=lambda role: ROLE_OPTIONS[role]["label"],
        horizontal=True,
        key="role",
        help=ROLE_OPTIONS[st.session_state.get("role", "student")]["help"],
    )

    st.markdown("---")
    st.subheader(f"{selected_role.capitalize()} Login")

    email = st.text_input("Email")
    password = st.text_input("Password", type="password")

    col1, col2 = st.columns(2)

    with col1:
        if st.button("Login", use_container_width=True):
            try:
                user = authenticate_user(email, password, selected_role)
                st.session_state.user = user
                st.rerun()
            except Exception:
                st.error("Invalid email or password")

    with col2:
        if st.button("Create Account", use_container_width=True):
            try:
                supabase.auth.sign_up({"email": email, "password": password})
                st.success("Account created! You can now log in.")
            except Exception:
                st.error("Signup failed")

    return None