import psycopg2
import os
from datetime import datetime, timedelta
import json

def get_db_connection():
    """Get database connection using environment variables"""
    try:
        conn = psycopg2.connect(
            host=os.getenv('PGHOST'),
            database=os.getenv('PGDATABASE'),
            user=os.getenv('PGUSER'),
            password=os.getenv('PGPASSWORD'),
            port=os.getenv('PGPORT', 5432)
        )
        return conn
    except Exception as e:
        print(f"Database connection error: {e}")
        return None

def init_database():
    """Initialize database tables"""
    conn = get_db_connection()
    if not conn:
        return False
    
    cur = None
    try:
        cur = conn.cursor()
        
        # Users table
        cur.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id SERIAL PRIMARY KEY,
                email VARCHAR(255) UNIQUE NOT NULL,
                username VARCHAR(100) NOT NULL,
                full_name VARCHAR(255),
                bio TEXT,
                genre VARCHAR(100),
                profile_image_url TEXT,
                social_links JSONB,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                trial_start_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                subscription_status VARCHAR(20) DEFAULT 'trial',
                last_payment_date TIMESTAMP,
                next_payment_due TIMESTAMP
            )
        """)
        
        # Tracks table
        cur.execute("""
            CREATE TABLE IF NOT EXISTS tracks (
                id SERIAL PRIMARY KEY,
                user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
                title VARCHAR(255) NOT NULL,
                artist VARCHAR(255) NOT NULL,
                album VARCHAR(255),
                genre VARCHAR(100),
                release_year INTEGER,
                producer_credits TEXT,
                featured_artists TEXT,
                lyrics TEXT,
                file_path TEXT NOT NULL,
                file_size INTEGER,
                duration_seconds INTEGER,
                cover_art_url TEXT,
                play_count INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Payment history table
        cur.execute("""
            CREATE TABLE IF NOT EXISTS payments (
                id SERIAL PRIMARY KEY,
                user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
                stripe_payment_id VARCHAR(255),
                amount DECIMAL(10, 2) NOT NULL,
                currency VARCHAR(3) DEFAULT 'NAD',
                status VARCHAR(20) NOT NULL,
                payment_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                subscription_period_start TIMESTAMP,
                subscription_period_end TIMESTAMP
            )
        """)
        
        # Analytics table
        cur.execute("""
            CREATE TABLE IF NOT EXISTS track_plays (
                id SERIAL PRIMARY KEY,
                track_id INTEGER REFERENCES tracks(id) ON DELETE CASCADE,
                user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
                ip_address INET,
                user_agent TEXT,
                played_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        conn.commit()
        cur.close()
        conn.close()
        return True
        
    except Exception as e:
        print(f"Database initialization error: {e}")
        conn.rollback()
        if cur:
            cur.close()
        conn.close()
        return False

def get_user_by_email(email):
    """Get user by email"""
    conn = get_db_connection()
    if not conn:
        return None
    
    cur = None
    try:
        cur = conn.cursor()
        cur.execute("SELECT * FROM users WHERE email = %s", (email,))
        user = cur.fetchone()
        cur.close()
        conn.close()
        
        if user:
            return {
                'id': user[0],
                'email': user[1],
                'username': user[2],
                'full_name': user[3],
                'bio': user[4],
                'genre': user[5],
                'profile_image_url': user[6],
                'social_links': user[7],
                'created_at': user[8],
                'trial_start_date': user[9],
                'subscription_status': user[10],
                'last_payment_date': user[11],
                'next_payment_due': user[12]
            }
        return None
        
    except Exception as e:
        print(f"Error getting user: {e}")
        if cur:
            cur.close()
        conn.close()
        return None

def create_user(email, username, full_name=None):
    """Create new user"""
    conn = get_db_connection()
    if not conn:
        return None
    
    cur = None
    try:
        cur = conn.cursor()
        trial_end = datetime.now() + timedelta(days=14)
        
        cur.execute("""
            INSERT INTO users (email, username, full_name, next_payment_due)
            VALUES (%s, %s, %s, %s)
            RETURNING id
        """, (email, username, full_name, trial_end))
        
        result = cur.fetchone()
        if result:
            user_id = result[0]
            conn.commit()
            cur.close()
            conn.close()
            
            return get_user_by_id(user_id)
        
        conn.rollback()
        cur.close()
        conn.close()
        return None
        
    except Exception as e:
        print(f"Error creating user: {e}")
        conn.rollback()
        if cur:
            cur.close()
        conn.close()
        return None

def get_user_by_id(user_id):
    """Get user by ID"""
    conn = get_db_connection()
    if not conn:
        return None
    
    cur = None
    try:
        cur = conn.cursor()
        cur.execute("SELECT * FROM users WHERE id = %s", (user_id,))
        user = cur.fetchone()
        cur.close()
        conn.close()
        
        if user:
            return {
                'id': user[0],
                'email': user[1],
                'username': user[2],
                'full_name': user[3],
                'bio': user[4],
                'genre': user[5],
                'profile_image_url': user[6],
                'social_links': user[7],
                'created_at': user[8],
                'trial_start_date': user[9],
                'subscription_status': user[10],
                'last_payment_date': user[11],
                'next_payment_due': user[12]
            }
        return None
        
    except Exception as e:
        print(f"Error getting user by ID: {e}")
        if cur:
            cur.close()
        conn.close()
        return None

def update_user_profile(user_id, bio=None, genre=None, social_links=None, profile_image_url=None):
    """Update user profile"""
    conn = get_db_connection()
    if not conn:
        return False
    
    cur = None
    try:
        cur = conn.cursor()
        
        update_fields = []
        params = []
        
        if bio is not None:
            update_fields.append("bio = %s")
            params.append(bio)
        
        if genre is not None:
            update_fields.append("genre = %s")
            params.append(genre)
        
        if social_links is not None:
            update_fields.append("social_links = %s")
            params.append(json.dumps(social_links))
        
        if profile_image_url is not None:
            update_fields.append("profile_image_url = %s")
            params.append(profile_image_url)
        
        if update_fields:
            params.append(user_id)
            query = f"UPDATE users SET {', '.join(update_fields)} WHERE id = %s"
            cur.execute(query, params)
            conn.commit()
        
        cur.close()
        conn.close()
        return True
        
    except Exception as e:
        print(f"Error updating user profile: {e}")
        conn.rollback()
        if cur:
            cur.close()
        conn.close()
        return False

def update_subscription_status(user_id, status, payment_date=None, next_due_date=None):
    """Update subscription status"""
    conn = get_db_connection()
    if not conn:
        return False
    
    cur = None
    try:
        cur = conn.cursor()
        
        if payment_date and next_due_date:
            cur.execute("""
                UPDATE users 
                SET subscription_status = %s, last_payment_date = %s, next_payment_due = %s
                WHERE id = %s
            """, (status, payment_date, next_due_date, user_id))
        else:
            cur.execute("""
                UPDATE users 
                SET subscription_status = %s
                WHERE id = %s
            """, (status, user_id))
        
        conn.commit()
        cur.close()
        conn.close()
        return True
        
    except Exception as e:
        print(f"Error updating subscription status: {e}")
        conn.rollback()
        if cur:
            cur.close()
        conn.close()
        return False

def create_track(user_id, title, artist, file_path, album=None, genre=None, 
                release_year=None, producer_credits=None, featured_artists=None, 
                lyrics=None, file_size=None, duration_seconds=None, cover_art_url=None):
    """Create new track"""
    conn = get_db_connection()
    if not conn:
        return None
    
    cur = None
    try:
        cur = conn.cursor()
        
        cur.execute("""
            INSERT INTO tracks (user_id, title, artist, album, genre, release_year,
                              producer_credits, featured_artists, lyrics, file_path,
                              file_size, duration_seconds, cover_art_url)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING id
        """, (user_id, title, artist, album, genre, release_year,
              producer_credits, featured_artists, lyrics, file_path,
              file_size, duration_seconds, cover_art_url))
        
        result = cur.fetchone()
        if result:
            track_id = result[0]
        else:
            conn.rollback()
            cur.close()
            conn.close()
            return None
        
        conn.commit()
        cur.close()
        conn.close()
        
        return track_id
        
    except Exception as e:
        print(f"Error creating track: {e}")
        conn.rollback()
        if cur:
            cur.close()
        conn.close()
        return None

def get_user_tracks(user_id):
    """Get all tracks for a user"""
    conn = get_db_connection()
    if not conn:
        return []
    
    cur = None
    try:
        cur = conn.cursor()
        cur.execute("""
            SELECT id, title, artist, album, genre, release_year, producer_credits,
                   featured_artists, lyrics, file_path, file_size, duration_seconds,
                   cover_art_url, play_count, created_at, updated_at
            FROM tracks 
            WHERE user_id = %s 
            ORDER BY created_at DESC
        """, (user_id,))
        
        tracks = cur.fetchall()
        cur.close()
        conn.close()
        
        return [{
            'id': track[0],
            'title': track[1],
            'artist': track[2],
            'album': track[3],
            'genre': track[4],
            'release_year': track[5],
            'producer_credits': track[6],
            'featured_artists': track[7],
            'lyrics': track[8],
            'file_path': track[9],
            'file_size': track[10],
            'duration_seconds': track[11],
            'cover_art_url': track[12],
            'play_count': track[13],
            'created_at': track[14],
            'updated_at': track[15]
        } for track in tracks]
        
    except Exception as e:
        print(f"Error getting user tracks: {e}")
        if cur:
            cur.close()
        conn.close()
        return []

def increment_play_count(track_id, ip_address=None, user_agent=None):
    """Increment play count for a track"""
    conn = get_db_connection()
    if not conn:
        return False
    
    cur = None
    try:
        cur = conn.cursor()
        
        # Update play count
        cur.execute("UPDATE tracks SET play_count = play_count + 1 WHERE id = %s", (track_id,))
        
        # Log the play
        cur.execute("""
            INSERT INTO track_plays (track_id, ip_address, user_agent)
            VALUES (%s, %s, %s)
        """, (track_id, ip_address, user_agent))
        
        conn.commit()
        cur.close()
        conn.close()
        return True
        
    except Exception as e:
        print(f"Error incrementing play count: {e}")
        conn.rollback()
        if cur:
            cur.close()
        conn.close()
        return False
