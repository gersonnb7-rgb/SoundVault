import streamlit as st
import json
from auth import require_auth
from database import update_user_profile, get_user_by_id

st.set_page_config(
    page_title="Profile - Omawi Na",
    page_icon="👤",
    layout="wide"
)

# Require authentication
user = require_auth()

st.title("👤 Your Musician Profile")

# Profile form
with st.form("profile_form"):
    st.subheader("📝 Basic Information")
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.markdown("**Profile Photo**")
        profile_image_url = st.text_input(
            "Profile Image URL",
            value=user.get('profile_image_url', '') or '',
            placeholder="https://example.com/your-photo.jpg"
        )
        
        if profile_image_url:
            try:
                st.image(profile_image_url, width=200, caption="Profile Preview")
            except:
                st.warning("Invalid image URL")
    
    with col2:
        st.markdown("**Artist Information**")
        
        # Display read-only info
        st.text_input("Username", value=user['username'], disabled=True)
        st.text_input("Email", value=user['email'], disabled=True)
        st.text_input("Full Name", value=user.get('full_name', '') or '', disabled=True)
        
        # Editable bio
        bio = st.text_area(
            "Artist Bio",
            value=user.get('bio', '') or '',
            placeholder="Tell the world about your music journey, influences, and style...",
            height=100
        )
        
        # Genre selection
        current_genre = user.get('genre', '') or ''
        genre = st.selectbox(
            "Primary Genre",
            ["", "Rock", "Pop", "Hip Hop", "Jazz", "Blues", "Electronic", "Country", 
             "Classical", "R&B", "Reggae", "Folk", "Punk", "Metal", "Indie", "Alternative",
             "Acoustic", "Experimental", "World Music", "Other"],
            index=0 if not current_genre else (
                ["", "Rock", "Pop", "Hip Hop", "Jazz", "Blues", "Electronic", "Country", 
                 "Classical", "R&B", "Reggae", "Folk", "Punk", "Metal", "Indie", "Alternative",
                 "Acoustic", "Experimental", "World Music", "Other"].index(current_genre) 
                if current_genre in ["", "Rock", "Pop", "Hip Hop", "Jazz", "Blues", "Electronic", "Country", 
                                   "Classical", "R&B", "Reggae", "Folk", "Punk", "Metal", "Indie", "Alternative",
                                   "Acoustic", "Experimental", "World Music", "Other"] else 0
            )
        )
    
    st.markdown("---")
    st.subheader("🌐 Social Media & Links")
    
    # Parse existing social links
    existing_links = user.get('social_links') or {}
    if isinstance(existing_links, str):
        try:
            existing_links = json.loads(existing_links)
        except:
            existing_links = {}
    
    col1, col2 = st.columns(2)
    
    with col1:
        spotify_url = st.text_input(
            "Spotify Profile",
            value=existing_links.get('spotify', ''),
            placeholder="https://open.spotify.com/artist/..."
        )
        
        youtube_url = st.text_input(
            "YouTube Channel",
            value=existing_links.get('youtube', ''),
            placeholder="https://youtube.com/@yourchannel"
        )
        
        soundcloud_url = st.text_input(
            "SoundCloud Profile",
            value=existing_links.get('soundcloud', ''),
            placeholder="https://soundcloud.com/yourprofile"
        )
    
    with col2:
        instagram_url = st.text_input(
            "Instagram",
            value=existing_links.get('instagram', ''),
            placeholder="https://instagram.com/yourhandle"
        )
        
        twitter_url = st.text_input(
            "Twitter/X",
            value=existing_links.get('twitter', ''),
            placeholder="https://twitter.com/yourhandle"
        )
        
        website_url = st.text_input(
            "Website",
            value=existing_links.get('website', ''),
            placeholder="https://yourwebsite.com"
        )
    
    # Submit button
    submitted = st.form_submit_button("💾 Update Profile", type="primary")
    
    if submitted:
        # Prepare social links data
        social_links = {}
        if spotify_url:
            social_links['spotify'] = spotify_url
        if youtube_url:
            social_links['youtube'] = youtube_url
        if soundcloud_url:
            social_links['soundcloud'] = soundcloud_url
        if instagram_url:
            social_links['instagram'] = instagram_url
        if twitter_url:
            social_links['twitter'] = twitter_url
        if website_url:
            social_links['website'] = website_url
        
        # Update profile
        success = update_user_profile(
            user['id'],
            bio=bio,
            genre=genre,
            social_links=social_links,
            profile_image_url=profile_image_url if profile_image_url else None
        )
        
        if success:
            st.success("✅ Profile updated successfully!")
            st.balloons()
            
            # Refresh user data
            st.session_state.user = get_user_by_id(user['id'])
            st.rerun()
        else:
            st.error("❌ Failed to update profile. Please try again.")

# Profile preview
st.markdown("---")
st.subheader("👁️ Profile Preview")

col1, col2 = st.columns([1, 2])

with col1:
    if user.get('profile_image_url'):
        try:
            st.image(user['profile_image_url'], width=200)
        except:
            st.image("https://via.placeholder.com/200x200?text=No+Image", width=200)
    else:
        st.image("https://via.placeholder.com/200x200?text=No+Image", width=200)

with col2:
    st.markdown(f"## {user['username']}")
    if user.get('full_name'):
        st.markdown(f"**{user['full_name']}**")
    
    if user.get('genre'):
        st.markdown(f"🎵 **Genre:** {user['genre']}")
    
    if user.get('bio'):
        st.markdown(f"**Bio:** {user['bio']}")
    else:
        st.markdown("*No bio added yet*")
    
    # Social links
    social_links = user.get('social_links') or {}
    if isinstance(social_links, str):
        try:
            social_links = json.loads(social_links)
        except:
            social_links = {}
    
    if social_links:
        st.markdown("**Links:**")
        for platform, url in social_links.items():
            if url:
                platform_name = platform.title()
                st.markdown(f"🔗 [{platform_name}]({url})")

# Portfolio link
st.markdown("---")
st.subheader("🌐 Public Portfolio")
portfolio_url = f"https://omawina.app/{user['username']}"
st.info(f"Your public portfolio: {portfolio_url}")

col1, col2 = st.columns(2)
with col1:
    if st.button("📋 Copy Portfolio Link", use_container_width=True):
        st.success("Portfolio link copied!")

with col2:
    if st.button("👁️ View Portfolio", use_container_width=True):
        st.switch_page("pages/5_Portfolio.py")
