import streamlit as st
import os
from datetime import datetime, timedelta
from auth import init_auth, get_current_user, logout_user
from database import init_database, get_user_by_email, create_user, update_subscription_status
from payment import check_subscription_status

# Initialize the application
def init_app():
    init_database()
    init_auth()

def main():
    st.set_page_config(
        page_title="Omawi Na - Music Hub for Musicians",
        page_icon="🎵",
        layout="wide"
    )
    
    init_app()
    
    # Check authentication
    user = get_current_user()
    
    if not user:
        show_landing_page()
    else:
        show_authenticated_app(user)

def show_landing_page():
    st.title("🎵 Omawi Na")
    st.subheader("A Professional Music Hub for Musicians")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("""
        ### Welcome to Omawi Na
        
        Omawi Na is your private, professional vault and portfolio for music. 
        Store, manage, and showcase your music catalog with these features:
        
        - 🎼 **Upload & Manage** your music collection (MP3, WAV, FLAC)
        - 👤 **Professional Profiles** with bio, photos, and social links
        - 🎵 **Built-in Audio Player** for streaming your tracks
        - 🌐 **Public Portfolio** with shareable artist links
        - 📊 **Track Analytics** and play statistics
        - 🔒 **Private Sharing** with password protection
        
        **14-day free trial** • **100 NAD quarterly subscription**
        """)
    
    with col2:
        st.markdown("### Get Started")
        if st.button("🎤 Sign Up as Musician", type="primary", use_container_width=True):
            # Redirect to Replit Auth
            st.info("Redirecting to authentication...")
            # In a real implementation, this would redirect to Replit Auth
            st.markdown("[Sign Up with Replit Auth](https://replit.com/auth)")
        
        if st.button("🎵 Sign In", use_container_width=True):
            st.info("Redirecting to authentication...")
            st.markdown("[Sign In with Replit Auth](https://replit.com/auth)")

def show_authenticated_app(user):
    # Check subscription status
    subscription_status = check_subscription_status(user['id'])
    
    # Show subscription warning if needed
    if subscription_status in ['grace_period', 'suspended']:
        if subscription_status == 'grace_period':
            st.warning("⚠️ Your subscription payment is overdue. Please update your payment to avoid account suspension.")
        else:
            st.error("🚫 Your account is suspended due to overdue payment. Please update your subscription to regain access.")
            st.stop()
    
    # Sidebar navigation
    with st.sidebar:
        st.title(f"Welcome, {user['username']}")
        st.write(f"Status: {subscription_status.replace('_', ' ').title()}")
        
        if st.button("🚪 Logout"):
            logout_user()
            st.rerun()
    
    # Main content
    st.title("🎵 Omawi Na Dashboard")
    
    # Quick stats
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Tracks", "0", "Upload your first track!")
    
    with col2:
        st.metric("Total Plays", "0")
    
    with col3:
        st.metric("Portfolio Views", "0")
    
    with col4:
        st.metric("Days Left in Trial" if subscription_status == 'trial' else "Subscription", 
              "14" if subscription_status == 'trial' else "Active")
    
    st.markdown("---")
    
    # Recent activity
    st.subheader("📈 Recent Activity")
    st.info("No recent activity. Start by uploading your first track!")
    
    # Quick actions
    st.subheader("🚀 Quick Actions")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("🎵 Upload New Track", type="primary", use_container_width=True):
            st.switch_page("pages/2_Upload_Music.py")
    
    with col2:
        if st.button("👤 Edit Profile", use_container_width=True):
            st.switch_page("pages/3_Profile.py")
    
    with col3:
        if st.button("🌐 View Portfolio", use_container_width=True):
            st.switch_page("pages/5_Portfolio.py")

if __name__ == "__main__":
    main()
