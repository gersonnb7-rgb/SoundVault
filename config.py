import os
from typing import Optional

class Config:
    SUPABASE_URL: str = os.getenv('SUPABASE_URL', '')
    SUPABASE_ANON_KEY: str = os.getenv('SUPABASE_ANON_KEY', '')

    STRIPE_SECRET_KEY: str = os.getenv('STRIPE_SECRET_KEY', 'sk_test_default_key')
    STRIPE_PUBLISHABLE_KEY: str = os.getenv('STRIPE_PUBLISHABLE_KEY', 'pk_test_default_key')

    SENDGRID_API_KEY: str = os.getenv('SENDGRID_API_KEY', 'default_key')
    SENDGRID_FROM_EMAIL: str = os.getenv('SENDGRID_FROM_EMAIL', 'noreply@omawina.app')

    MAX_FILE_SIZE_MB: int = 50
    ALLOWED_AUDIO_FORMATS: list = ['mp3', 'wav', 'flac']

    TRIAL_PERIOD_DAYS: int = 14
    GRACE_PERIOD_DAYS: int = 7
    SUBSCRIPTION_AMOUNT_NAD: int = 100
    SUBSCRIPTION_PERIOD_DAYS: int = 90

    UPLOAD_DIR: str = 'uploads'

    APP_NAME: str = 'Omawi Na'
    APP_DESCRIPTION: str = 'Professional Music Hub for Musicians'

    @classmethod
    def is_production(cls) -> bool:
        return os.getenv('ENVIRONMENT', 'development') == 'production'

    @classmethod
    def is_demo_mode(cls) -> bool:
        return cls.STRIPE_SECRET_KEY == 'sk_test_default_key'

    @classmethod
    def validate(cls) -> tuple[bool, list[str]]:
        errors = []

        if not cls.SUPABASE_URL:
            errors.append("SUPABASE_URL is not set")

        if not cls.SUPABASE_ANON_KEY:
            errors.append("SUPABASE_ANON_KEY is not set")

        if cls.is_production() and cls.STRIPE_SECRET_KEY.startswith('sk_test_'):
            errors.append("Production environment requires production Stripe key")

        return len(errors) == 0, errors

config = Config()
