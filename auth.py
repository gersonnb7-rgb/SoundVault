import streamlit as st
import os
from database import get_user_by_email, create_user

def init_auth():
    """Initialize authentication session"""
    if 'user' not in st.session_state:
        st.session_state.user = None
    
    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = False

def get_current_user():
    """Get current authenticated user"""
    # In a real implementation, this would integrate with Replit Auth
    # For now, we'll simulate with session state
    
    if st.session_state.get('authenticated', False):
        return st.session_state.get('user')
    
    # Check if we have auth info from Replit (this would be handled by Replit Auth)
    # For demonstration, we'll use a simulated approach
    if 'demo_user_email' in st.query_params:
        email = st.query_params['demo_user_email']
        username = st.query_params.get('demo_user_name', email.split('@')[0])
        
        # Get or create user
        user = get_user_by_email(email)
        if not user:
            user = create_user(email, username)
        
        if user:
            st.session_state.user = user
            st.session_state.authenticated = True
            return user
    
    return None

def login_user(email, username, full_name=None):
    """Login or create user"""
    user = get_user_by_email(email)
    
    if not user:
        user = create_user(email, username, full_name)
    
    if user:
        st.session_state.user = user
        st.session_state.authenticated = True
        return user
    
    return None

def logout_user():
    """Logout current user"""
    st.session_state.user = None
    st.session_state.authenticated = False

def require_auth():
    """Decorator to require authentication"""
    user = get_current_user()
    if not user:
        st.error("Please sign in to access this page.")
        st.stop()
    return user

def get_replit_auth_info():
    """Get authentication info from Replit Auth headers"""
    # In a real implementation, this would read from Replit Auth headers
    # For now, return None to simulate unauthenticated state
    return None
