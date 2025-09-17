import streamlit as st
import os
from auth import require_auth
from database import create_track
from payment import check_subscription_status
from audio_utils import validate_audio_file, get_audio_metadata, save_uploaded_file

st.set_page_config(
    page_title="Upload Music - SoundVault",
    page_icon="🎵",
    layout="wide"
)

# Require authentication
user = require_auth()

# Check subscription status
subscription_status = check_subscription_status(user['id'])

if subscription_status == 'suspended':
    st.error("🚫 Your account is suspended. Please update your payment to upload music.")
    st.stop()

st.title("🎵 Upload New Track")

if subscription_status == 'grace_period':
    st.warning("⚠️ Your payment is overdue. Please update your subscription to avoid account suspension.")

# Upload form
with st.form("upload_track_form", clear_on_submit=True):
    st.subheader("📁 Select Audio File")
    
    uploaded_file = st.file_uploader(
        "Choose an audio file",
        type=['mp3', 'wav', 'flac'],
        help="Supported formats: MP3, WAV, FLAC (Max 50MB)"
    )
    
    # Metadata section
    st.subheader("📝 Track Information")
    
    col1, col2 = st.columns(2)
    
    with col1:
        title = st.text_input("Track Title *", placeholder="Enter track title")
        artist = st.text_input("Artist *", value=user.get('username', ''), placeholder="Artist name")
        album = st.text_input("Album", placeholder="Album name (optional)")
        genre = st.selectbox(
            "Genre",
            ["", "Rock", "Pop", "Hip Hop", "Jazz", "Blues", "Electronic", "Country", 
             "Classical", "R&B", "Reggae", "Folk", "Punk", "Metal", "Indie", "Other"]
        )
    
    with col2:
        release_year = st.number_input(
            "Release Year", 
            min_value=1900, 
            max_value=2030, 
            value=None,
            placeholder="YYYY"
        )
        producer_credits = st.text_input("Producer Credits", placeholder="Producer name (optional)")
        featured_artists = st.text_input("Featured Artists", placeholder="Featured artists (optional)")
        cover_art_url = st.text_input("Cover Art URL", placeholder="HTTP URL to cover art (optional)")
    
    # Lyrics section
    st.subheader("📄 Lyrics (Optional)")
    lyrics = st.text_area("Lyrics", placeholder="Enter song lyrics here...", height=100)
    
    # Submit button
    submit_button = st.form_submit_button("🎵 Upload Track", type="primary")
    
    if submit_button:
        # Validation
        if not uploaded_file:
            st.error("Please select an audio file to upload.")
        elif not title:
            st.error("Track title is required.")
        elif not artist:
            st.error("Artist name is required.")
        else:
            # Validate file
            is_valid, message = validate_audio_file(uploaded_file)
            
            if not is_valid:
                st.error(message)
            else:
                with st.spinner("Uploading and processing your track..."):
                    try:
                        # Create temporary file to extract metadata
                        temp_path = f"/tmp/{uploaded_file.name}"
                        with open(temp_path, "wb") as f:
                            f.write(uploaded_file.getbuffer())
                        
                        # Extract metadata from file
                        file_metadata = get_audio_metadata(temp_path)
                        
                        # Use extracted metadata if fields are empty
                        if not title and file_metadata.get('title'):
                            title = file_metadata['title']
                        if not artist and file_metadata.get('artist'):
                            artist = file_metadata['artist']
                        if not album and file_metadata.get('album'):
                            album = file_metadata['album']
                        if not genre and file_metadata.get('genre'):
                            genre = file_metadata['genre']
                        if not release_year and file_metadata.get('year'):
                            try:
                                release_year = int(file_metadata['year'][:4])
                            except:
                                pass
                        
                        # Create track record in database
                        track_id = create_track(
                            user_id=user['id'],
                            title=title,
                            artist=artist,
                            album=album,
                            genre=genre,
                            release_year=release_year,
                            producer_credits=producer_credits,
                            featured_artists=featured_artists,
                            lyrics=lyrics,
                            file_path="",  # Will be updated after saving
                            file_size=uploaded_file.size,
                            duration_seconds=file_metadata.get('duration'),
                            cover_art_url=cover_art_url if cover_art_url else None
                        )
                        
                        if track_id:
                            # Save the actual file
                            file_path = save_uploaded_file(uploaded_file, user['id'], track_id)
                            
                            if file_path:
                                # Update track with file path
                                from database import get_db_connection
                                conn = get_db_connection()
                                if conn:
                                    cur = conn.cursor()
                                    cur.execute(
                                        "UPDATE tracks SET file_path = %s WHERE id = %s",
                                        (file_path, track_id)
                                    )
                                    conn.commit()
                                    cur.close()
                                    conn.close()
                                
                                st.success("🎉 Track uploaded successfully!")
                                st.balloons()
                                
                                # Show track details
                                st.subheader("✅ Upload Summary")
                                col1, col2 = st.columns(2)
                                
                                with col1:
                                    st.info(f"**Title:** {title}")
                                    st.info(f"**Artist:** {artist}")
                                    if album:
                                        st.info(f"**Album:** {album}")
                                    if genre:
                                        st.info(f"**Genre:** {genre}")
                                
                                with col2:
                                    if release_year:
                                        st.info(f"**Year:** {release_year}")
                                    st.info(f"**File Size:** {uploaded_file.size / (1024*1024):.2f} MB")
                                    if file_metadata.get('duration'):
                                        minutes = int(file_metadata['duration'] // 60)
                                        seconds = int(file_metadata['duration'] % 60)
                                        st.info(f"**Duration:** {minutes}:{seconds:02d}")
                                
                                # Navigation buttons
                                col1, col2 = st.columns(2)
                                with col1:
                                    if st.button("📊 Go to Dashboard", type="primary"):
                                        st.switch_page("pages/1_Dashboard.py")
                                with col2:
                                    if st.button("🎵 Upload Another Track"):
                                        st.rerun()
                            else:
                                st.error("Failed to save the uploaded file. Please try again.")
                        else:
                            st.error("Failed to create track record. Please try again.")
                        
                        # Clean up temp file
                        try:
                            os.remove(temp_path)
                        except:
                            pass
                            
                    except Exception as e:
                        st.error(f"An error occurred during upload: {str(e)}")

# Tips section
st.markdown("---")
st.subheader("💡 Upload Tips")

col1, col2 = st.columns(2)

with col1:
    st.markdown("""
    **File Requirements:**
    - Supported formats: MP3, WAV, FLAC
    - Maximum file size: 50 MB
    - High-quality audio recommended
    """)

with col2:
    st.markdown("""
    **Best Practices:**
    - Include complete metadata
    - Use descriptive track titles
    - Add album art URL for better presentation
    """)
