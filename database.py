from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any
from supabase_client import get_supabase_client
import json

def init_database():
    try:
        client = get_supabase_client()
        return True
    except Exception as e:
        print(f"Database initialization error: {e}")
        return False

def get_user_by_email(email: str) -> Optional[Dict[str, Any]]:
    try:
        client = get_supabase_client()
        response = client.table('users').select('*').eq('email', email).maybeSingle().execute()

        return response.data if response.data else None

    except Exception as e:
        print(f"Error getting user by email: {e}")
        return None

def get_user_by_id(user_id: str) -> Optional[Dict[str, Any]]:
    try:
        client = get_supabase_client()
        response = client.table('users').select('*').eq('id', user_id).maybeSingle().execute()

        return response.data if response.data else None

    except Exception as e:
        print(f"Error getting user by ID: {e}")
        return None

def create_user(email: str, username: str, full_name: Optional[str] = None) -> Optional[Dict[str, Any]]:
    try:
        client = get_supabase_client()
        trial_end = datetime.now() + timedelta(days=14)

        user_data = {
            'email': email,
            'username': username,
            'full_name': full_name,
            'next_payment_due': trial_end.isoformat(),
            'subscription_status': 'trial'
        }

        response = client.table('users').insert(user_data).execute()

        if response.data and len(response.data) > 0:
            return response.data[0]

        return None

    except Exception as e:
        print(f"Error creating user: {e}")
        return None

def update_user_profile(
    user_id: str,
    bio: Optional[str] = None,
    genre: Optional[str] = None,
    social_links: Optional[Dict] = None,
    profile_image_url: Optional[str] = None
) -> bool:
    try:
        client = get_supabase_client()

        update_data = {}

        if bio is not None:
            update_data['bio'] = bio

        if genre is not None:
            update_data['genre'] = genre

        if social_links is not None:
            update_data['social_links'] = social_links

        if profile_image_url is not None:
            update_data['profile_image_url'] = profile_image_url

        if update_data:
            client.table('users').update(update_data).eq('id', user_id).execute()

        return True

    except Exception as e:
        print(f"Error updating user profile: {e}")
        return False

def update_subscription_status(
    user_id: str,
    status: str,
    payment_date: Optional[datetime] = None,
    next_due_date: Optional[datetime] = None
) -> bool:
    try:
        client = get_supabase_client()

        update_data = {'subscription_status': status}

        if payment_date:
            update_data['last_payment_date'] = payment_date.isoformat()

        if next_due_date:
            update_data['next_payment_due'] = next_due_date.isoformat()

        client.table('users').update(update_data).eq('id', user_id).execute()

        return True

    except Exception as e:
        print(f"Error updating subscription status: {e}")
        return False

def create_track(
    user_id: str,
    title: str,
    artist: str,
    file_path: str,
    album: Optional[str] = None,
    genre: Optional[str] = None,
    release_year: Optional[int] = None,
    producer_credits: Optional[str] = None,
    featured_artists: Optional[str] = None,
    lyrics: Optional[str] = None,
    file_size: Optional[int] = None,
    duration_seconds: Optional[int] = None,
    cover_art_url: Optional[str] = None
) -> Optional[str]:
    try:
        client = get_supabase_client()

        track_data = {
            'user_id': user_id,
            'title': title,
            'artist': artist,
            'file_path': file_path,
            'album': album,
            'genre': genre,
            'release_year': release_year,
            'producer_credits': producer_credits,
            'featured_artists': featured_artists,
            'lyrics': lyrics,
            'file_size': file_size,
            'duration_seconds': duration_seconds,
            'cover_art_url': cover_art_url
        }

        response = client.table('tracks').insert(track_data).execute()

        if response.data and len(response.data) > 0:
            return response.data[0]['id']

        return None

    except Exception as e:
        print(f"Error creating track: {e}")
        return None

def get_user_tracks(user_id: str) -> List[Dict[str, Any]]:
    try:
        client = get_supabase_client()
        response = client.table('tracks').select('*').eq('user_id', user_id).order('created_at', desc=True).execute()

        return response.data if response.data else []

    except Exception as e:
        print(f"Error getting user tracks: {e}")
        return []

def update_track_file_path(track_id: str, file_path: str) -> bool:
    try:
        client = get_supabase_client()
        client.table('tracks').update({'file_path': file_path}).eq('id', track_id).execute()

        return True

    except Exception as e:
        print(f"Error updating track file path: {e}")
        return False

def increment_play_count(track_id: str, ip_address: Optional[str] = None, user_agent: Optional[str] = None) -> bool:
    try:
        client = get_supabase_client()

        track = client.table('tracks').select('play_count').eq('id', track_id).maybeSingle().execute()

        if track.data:
            new_count = (track.data.get('play_count') or 0) + 1
            client.table('tracks').update({'play_count': new_count}).eq('id', track_id).execute()

        play_data = {
            'track_id': track_id,
            'ip_address': ip_address,
            'user_agent': user_agent
        }

        client.table('track_plays').insert(play_data).execute()

        return True

    except Exception as e:
        print(f"Error incrementing play count: {e}")
        return False

def record_payment(
    user_id: str,
    stripe_payment_id: str,
    amount: float,
    status: str,
    payment_date: datetime,
    period_end: datetime
) -> bool:
    try:
        client = get_supabase_client()

        payment_data = {
            'user_id': user_id,
            'stripe_payment_id': stripe_payment_id,
            'amount': amount,
            'status': status,
            'payment_date': payment_date.isoformat(),
            'subscription_period_start': payment_date.isoformat(),
            'subscription_period_end': period_end.isoformat()
        }

        client.table('payments').insert(payment_data).execute()

        return True

    except Exception as e:
        print(f"Error recording payment: {e}")
        return False

def get_payment_history(user_id: str) -> List[Dict[str, Any]]:
    try:
        client = get_supabase_client()
        response = client.table('payments').select('*').eq('user_id', user_id).order('payment_date', desc=True).execute()

        return response.data if response.data else []

    except Exception as e:
        print(f"Error getting payment history: {e}")
        return []
