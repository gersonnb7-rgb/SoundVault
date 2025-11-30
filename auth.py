import streamlit as st
from database import get_user_by_email, create_user
from typing import Optional, Dict, Any

def init_auth():
    if 'user' not in st.session_state:
        st.session_state.user = None

    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = False

def get_current_user() -> Optional[Dict[str, Any]]:
    if st.session_state.get('authenticated', False):
        return st.session_state.get('user')

    if 'demo_user_email' in st.query_params:
        email = st.query_params['demo_user_email']
        username = st.query_params.get('demo_user_name', email.split('@')[0])

        user = get_user_by_email(email)
        if not user:
            user = create_user(email, username)

        if user:
            st.session_state.user = user
            st.session_state.authenticated = True
            return user

    return None

def login_user(email: str, username: str, full_name: Optional[str] = None) -> Optional[Dict[str, Any]]:
    user = get_user_by_email(email)

    if not user:
        user = create_user(email, username, full_name)

    if user:
        st.session_state.user = user
        st.session_state.authenticated = True
        return user

    return None

def logout_user():
    st.session_state.user = None
    st.session_state.authenticated = False

def require_auth() -> Dict[str, Any]:
    user = get_current_user()
    if not user:
        st.error("Please sign in to access this page.")
        st.info("For demo purposes, add ?demo_user_email=test@example.com to the URL")
        st.stop()
    return user
