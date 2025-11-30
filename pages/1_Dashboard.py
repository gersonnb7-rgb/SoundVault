import streamlit as st
from auth import require_auth
from database import get_user_tracks
from payment import check_subscription_status, calculate_days_remaining
from audio_utils import format_duration, get_file_size_mb

st.set_page_config(
    page_title="Dashboard - Omawi Na",
    page_icon="🎵",
    layout="wide"
)

# Require authentication
user = require_auth()

# Check subscription status
subscription_status = check_subscription_status(user['id'])

st.title("🎵 Your Music Dashboard")

# Subscription status banner
if subscription_status == 'trial':
    days_remaining = calculate_days_remaining(user)
    st.info(f"🆓 Free Trial - {days_remaining} days remaining")
elif subscription_status == 'grace_period':
    st.warning("⚠️ Payment overdue - Account in grace period")
elif subscription_status == 'suspended':
    st.error("🚫 Account suspended - Please update payment")
    st.stop()
else:
    st.success("✅ Subscription Active")

# Get user tracks
tracks = get_user_tracks(user['id'])

# Statistics
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("Total Tracks", len(tracks))

with col2:
    total_plays = sum(track['play_count'] for track in tracks)
    st.metric("Total Plays", total_plays)

with col3:
    total_duration = sum(track['duration_seconds'] or 0 for track in tracks)
    st.metric("Total Duration", format_duration(total_duration))

with col4:
    total_size = sum(track['file_size'] or 0 for track in tracks)
    st.metric("Storage Used", f"{get_file_size_mb(total_size)} MB")

st.markdown("---")

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

# Recent tracks
st.subheader("🎼 Your Music Library")

if not tracks:
    st.info("No tracks uploaded yet. Upload your first track to get started!")
else:
    # Display tracks in a grid
    for i in range(0, len(tracks), 2):
        col1, col2 = st.columns(2)
        
        # First track in row
        track = tracks[i]
        with col1:
            with st.container():
                st.markdown(f"### 🎵 {track['title']}")
                st.markdown(f"**Artist:** {track['artist']}")
                
                if track['album']:
                    st.markdown(f"**Album:** {track['album']}")
                
                if track['genre']:
                    st.markdown(f"**Genre:** {track['genre']}")
                
                col_info1, col_info2 = st.columns(2)
                
                with col_info1:
                    st.markdown(f"**Plays:** {track['play_count']}")
                    if track['duration_seconds']:
                        st.markdown(f"**Duration:** {format_duration(track['duration_seconds'])}")
                
                with col_info2:
                    if track['release_year']:
                        st.markdown(f"**Year:** {track['release_year']}")
                    if track['file_size']:
                        st.markdown(f"**Size:** {get_file_size_mb(track['file_size'])} MB")
                
                # Audio player placeholder
                if track['file_path']:
                    st.audio(track['file_path'])
                
                st.markdown(f"*Uploaded: {track['created_at'].strftime('%Y-%m-%d')}*")
        
        # Second track in row (if exists)
        if i + 1 < len(tracks):
            track = tracks[i + 1]
            with col2:
                with st.container():
                    st.markdown(f"### 🎵 {track['title']}")
                    st.markdown(f"**Artist:** {track['artist']}")
                    
                    if track['album']:
                        st.markdown(f"**Album:** {track['album']}")
                    
                    if track['genre']:
                        st.markdown(f"**Genre:** {track['genre']}")
                    
                    col_info1, col_info2 = st.columns(2)
                    
                    with col_info1:
                        st.markdown(f"**Plays:** {track['play_count']}")
                        if track['duration_seconds']:
                            st.markdown(f"**Duration:** {format_duration(track['duration_seconds'])}")
                    
                    with col_info2:
                        if track['release_year']:
                            st.markdown(f"**Year:** {track['release_year']}")
                        if track['file_size']:
                            st.markdown(f"**Size:** {get_file_size_mb(track['file_size'])} MB")
                    
                    # Audio player placeholder
                    if track['file_path']:
                        st.audio(track['file_path'])
                    
                    st.markdown(f"*Uploaded: {track['created_at'].strftime('%Y-%m-%d')}*")
        
        st.markdown("---")

# Portfolio link
st.subheader("🌐 Your Public Portfolio")
portfolio_url = f"https://omawina.app/{user['username']}"
st.info(f"Share your music: {portfolio_url}")

if st.button("📋 Copy Portfolio Link", use_container_width=True):
    st.success("Portfolio link copied to clipboard!")
