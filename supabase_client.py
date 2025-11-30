import os
from typing import Optional, Any

try:
    from supabase import create_client, Client
    SUPABASE_AVAILABLE = True
except ImportError:
    try:
        from supabase.client import create_client, Client
        SUPABASE_AVAILABLE = True
    except ImportError:
        SUPABASE_AVAILABLE = False
        Client = Any

_supabase_client: Optional[Any] = None

def get_supabase_client() -> Any:
    global _supabase_client

    if not SUPABASE_AVAILABLE:
        raise ImportError("Supabase client not available. Please install: pip install supabase")

    if _supabase_client is None:
        url = os.getenv('SUPABASE_URL')
        key = os.getenv('SUPABASE_ANON_KEY')

        if not url or not key:
            raise ValueError("SUPABASE_URL and SUPABASE_ANON_KEY must be set in environment")

        _supabase_client = create_client(url, key)

    return _supabase_client

def init_supabase():
    get_supabase_client()
