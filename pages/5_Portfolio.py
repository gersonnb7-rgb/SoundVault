import streamlit as st
import json
from auth import require_auth
from database import get_user_tracks, increment_play_count
from audio_utils import format_duration

st.set_page_config(
    page_title="Portfolio - Omawi Na",
    page_icon="🌐",
    layout="wide"
)

# Require authentication
user = require_auth()

# Get user tracks
tracks = get_user_tracks(user['id'])

# Portfolio header
st.markdown(f"# 🎵 {user['username']}")

if user.get('full_name'):
    st.markdown(f"## {user['full_name']}")

# Profile section
col1, col2 = st.columns([1, 3])

with col1:
    if user.get('profile_image_url'):
        try:
            st.image(user['profile_image_url'], width=200)
        except:
            st.image("https://via.placeholder.com/200x200?text=No+Image", width=200)
    else:
        st.image("https://via.placeholder.com/200x200?text=No+Image", width=200)

with col2:
    if user.get('genre'):
        st.markdown(f"### 🎵 {user['genre']} Artist")
    
    if user.get('bio'):
        st.markdown(user['bio'])
    else:
        st.markdown("*This artist hasn't added a bio yet.*")
    
    # Statistics
    col_stat1, col_stat2, col_stat3 = st.columns(3)
    
    with col_stat1:
        st.metric("Total Tracks", len(tracks))
    
    with col_stat2:
        total_plays = sum(track['play_count'] for track in tracks)
        st.metric("Total Plays", total_plays)
    
    with col_stat3:
        total_duration = sum(track['duration_seconds'] or 0 for track in tracks)
        st.metric("Total Duration", format_duration(total_duration))

# Social links
social_links = user.get('social_links') or {}
if isinstance(social_links, str):
    try:
        social_links = json.loads(social_links)
    except:
        social_links = {}

if social_links:
    st.markdown("---")
    st.subheader("🔗 Connect with the Artist")
    
    # Create columns for social links
    link_cols = st.columns(len(social_links))
    
    for i, (platform, url) in enumerate(social_links.items()):
        if url:
            with link_cols[i]:
                platform_icons = {
                    'spotify': '🎵',
                    'youtube': '📺',
                    'soundcloud': '🔊',
                    'instagram': '📷',
                    'twitter': '🐦',
                    'website': '🌐'
                }
                icon = platform_icons.get(platform, '🔗')
                if st.button(f"{icon} {platform.title()}", use_container_width=True):
                    st.markdown(f"[Open {platform.title()}]({url})")

# Music section
st.markdown("---")
st.subheader("🎼 Music Collection")

if not tracks:
    st.info("This artist hasn't uploaded any tracks yet.")
else:
    # Track list
    for track in tracks:
        with st.container():
            # Track header
            col1, col2 = st.columns([3, 1])
            
            with col1:
                st.markdown(f"### 🎵 {track['title']}")
                track_info = f"**Artist:** {track['artist']}"
                
                if track['album']:
                    track_info += f" • **Album:** {track['album']}"
                
                if track['genre']:
                    track_info += f" • **Genre:** {track['genre']}"
                
                if track['release_year']:
                    track_info += f" • **Year:** {track['release_year']}"
                
                st.markdown(track_info)
            
            with col2:
                st.markdown(f"**{track['play_count']} plays**")
                if track['duration_seconds']:
                    st.markdown(f"**{format_duration(track['duration_seconds'])}**")
            
            # Audio player
            if track['file_path']:
                # Create audio player
                audio_col1, audio_col2 = st.columns([4, 1])
                
                with audio_col1:
                    st.audio(track['file_path'])
                
                with audio_col2:
                    if st.button("▶️ Play", key=f"play_{track['id']}"):
                        # Increment play count
                        increment_play_count(track['id'])
                        st.success("Playing track!")
                        st.rerun()
            
            # Additional track info
            if track['producer_credits'] or track['featured_artists']:
                with st.expander("Track Credits"):
                    if track['producer_credits']:
                        st.markdown(f"**Producer:** {track['producer_credits']}")
                    if track['featured_artists']:
                        st.markdown(f"**Featured Artists:** {track['featured_artists']}")
            
            # Lyrics
            if track['lyrics']:
                with st.expander("View Lyrics"):
                    st.text(track['lyrics'])
            
            st.markdown("---")

# Portfolio sharing
st.markdown("---")
st.subheader("📱 Share This Portfolio")

portfolio_url = f"https://omawina.app/{user['username']}"

col1, col2 = st.columns([2, 1])

with col1:
    st.code(portfolio_url)

with col2:
    if st.button("📋 Copy Link", use_container_width=True):
        st.success("Portfolio link copied to clipboard!")

# Social sharing buttons
st.markdown("### Share on Social Media")

col1, col2, col3 = st.columns(3)

with col1:
    twitter_text = f"Check out {user['username']}'s music portfolio on Omawi Na!"
    twitter_url = f"https://twitter.com/intent/tweet?text={twitter_text}&url={portfolio_url}"
    if st.button("🐦 Share on Twitter", use_container_width=True):
        st.markdown(f"[Open Twitter]({twitter_url})")

with col2:
    facebook_url = f"https://www.facebook.com/sharer/sharer.php?u={portfolio_url}"
    if st.button("📘 Share on Facebook", use_container_width=True):
        st.markdown(f"[Open Facebook]({facebook_url})")

with col3:
    if st.button("📧 Share via Email", use_container_width=True):
        email_subject = f"Check out {user['username']}'s music"
        email_body = f"I thought you'd enjoy {user['username']}'s music portfolio: {portfolio_url}"
        email_url = f"mailto:?subject={email_subject}&body={email_body}"
        st.markdown(f"[Open Email]({email_url})")

# Footer
st.markdown("---")
st.markdown(
    f"<div style='text-align: center; color: #666; font-size: 0.9em;'>"
    f"Powered by <strong>Omawi Na</strong> • Professional Music Hub for Musicians"
    f"</div>", 
    unsafe_allow_html=True
)
