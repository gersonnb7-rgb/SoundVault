import os
from mutagen._file import File
from mutagen.id3._util import ID3NoHeaderError
import streamlit as st

def get_audio_metadata(file_path):
    """Extract metadata from audio file"""
    try:
        audio_file = File(file_path)
        
        if audio_file is None:
            return {}
        
        metadata = {}
        
        # Extract common metadata
        if audio_file.get('TIT2'):  # Title
            metadata['title'] = str(audio_file['TIT2'][0])
        elif audio_file.get('TITLE'):
            metadata['title'] = str(audio_file['TITLE'][0])
        
        if audio_file.get('TPE1'):  # Artist
            metadata['artist'] = str(audio_file['TPE1'][0])
        elif audio_file.get('ARTIST'):
            metadata['artist'] = str(audio_file['ARTIST'][0])
        
        if audio_file.get('TALB'):  # Album
            metadata['album'] = str(audio_file['TALB'][0])
        elif audio_file.get('ALBUM'):
            metadata['album'] = str(audio_file['ALBUM'][0])
        
        if audio_file.get('TCON'):  # Genre
            metadata['genre'] = str(audio_file['TCON'][0])
        elif audio_file.get('GENRE'):
            metadata['genre'] = str(audio_file['GENRE'][0])
        
        if audio_file.get('TDRC'):  # Year
            metadata['year'] = str(audio_file['TDRC'][0])
        elif audio_file.get('DATE'):
            metadata['year'] = str(audio_file['DATE'][0])
        
        # Duration
        if hasattr(audio_file, 'info') and hasattr(audio_file.info, 'length'):
            metadata['duration'] = int(audio_file.info.length)
        
        return metadata
        
    except Exception as e:
        st.error(f"Error reading audio metadata: {e}")
        return {}

def validate_audio_file(uploaded_file):
    """Validate uploaded audio file"""
    if uploaded_file is None:
        return False, "No file uploaded"
    
    # Check file extension
    allowed_extensions = ['.mp3', '.wav', '.flac']
    file_extension = os.path.splitext(uploaded_file.name)[1].lower()
    
    if file_extension not in allowed_extensions:
        return False, f"File type {file_extension} not supported. Please upload MP3, WAV, or FLAC files."
    
    # Check file size (max 50MB)
    max_size = 50 * 1024 * 1024  # 50MB in bytes
    if uploaded_file.size > max_size:
        return False, "File size too large. Maximum size is 50MB."
    
    return True, "File is valid"

def save_uploaded_file(uploaded_file, user_id, track_id):
    """Save uploaded file to disk"""
    try:
        # Create uploads directory if it doesn't exist
        upload_dir = "uploads"
        if not os.path.exists(upload_dir):
            os.makedirs(upload_dir)
        
        # Create user directory
        user_dir = os.path.join(upload_dir, str(user_id))
        if not os.path.exists(user_dir):
            os.makedirs(user_dir)
        
        # Generate file path
        file_extension = os.path.splitext(uploaded_file.name)[1]
        file_path = os.path.join(user_dir, f"track_{track_id}{file_extension}")
        
        # Save file
        with open(file_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        
        return file_path
        
    except Exception as e:
        st.error(f"Error saving file: {e}")
        return None

def format_duration(seconds):
    """Format duration in seconds to MM:SS format"""
    if not seconds:
        return "0:00"
    
    minutes = int(seconds // 60)
    seconds = int(seconds % 60)
    return f"{minutes}:{seconds:02d}"

def get_file_size_mb(file_size_bytes):
    """Convert file size from bytes to MB"""
    if not file_size_bytes:
        return 0
    return round(file_size_bytes / (1024 * 1024), 2)

def generate_audio_player_html(file_path, track_title):
    """Generate HTML audio player"""
    return f"""
    <audio controls style="width: 100%;">
        <source src="/{file_path}" type="audio/mpeg">
        <source src="/{file_path}" type="audio/wav">
        <source src="/{file_path}" type="audio/flac">
        Your browser does not support the audio element.
    </audio>
    <p style="margin-top: 5px; font-size: 0.9em; color: #666;">
        🎵 {track_title}
    </p>
    """
