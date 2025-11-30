import stripe
import os
from datetime import datetime, timedelta
from database import update_subscription_status, get_user_by_id, record_payment, get_payment_history
from typing import Optional, Dict, Any

stripe.api_key = os.getenv('STRIPE_SECRET_KEY', 'sk_test_default_key')

def check_subscription_status(user_id: str) -> str:
    user = get_user_by_id(user_id)
    if not user:
        return 'unknown'

    now = datetime.now()
    trial_start = user.get('trial_start_date')
    if isinstance(trial_start, str):
        trial_start = datetime.fromisoformat(trial_start.replace('Z', '+00:00'))

    next_payment_due = user.get('next_payment_due')
    if isinstance(next_payment_due, str):
        next_payment_due = datetime.fromisoformat(next_payment_due.replace('Z', '+00:00'))

    current_status = user.get('subscription_status', 'trial')

    if current_status == 'trial':
        trial_end = trial_start + timedelta(days=14) if trial_start else now
        if now < trial_end:
            return 'trial'
        else:
            last_payment = user.get('last_payment_date')
            if last_payment:
                return 'active'
            else:
                update_subscription_status(user_id, 'grace_period')
                return 'grace_period'

    if next_payment_due and now > next_payment_due:
        if current_status == 'active':
            update_subscription_status(user_id, 'grace_period')
            return 'grace_period'
        elif current_status == 'grace_period':
            grace_end = next_payment_due + timedelta(days=7)
            if now > grace_end:
                update_subscription_status(user_id, 'suspended')
                return 'suspended'
            return 'grace_period'

    return current_status

def create_payment_intent(user_id: str, amount_nad: int = 100) -> Optional[Dict[str, Any]]:
    try:
        amount_cents = int(amount_nad * 100)

        intent = stripe.PaymentIntent.create(
            amount=amount_cents,
            currency='nad',
            metadata={
                'user_id': str(user_id),
                'subscription_type': 'quarterly'
            }
        )

        return {
            'client_secret': intent.client_secret,
            'payment_intent_id': intent.id
        }

    except Exception as e:
        print(f"Stripe payment intent error: {e}")
        return None

def confirm_payment(payment_intent_id: str, user_id: str) -> bool:
    try:
        intent = stripe.PaymentIntent.retrieve(payment_intent_id)

        if intent.status == 'succeeded':
            now = datetime.now()
            next_due = now + timedelta(days=90)

            success = update_subscription_status(
                user_id,
                'active',
                payment_date=now,
                next_due_date=next_due
            )

            if success:
                record_payment(user_id, intent.id, intent.amount / 100, 'succeeded', now, next_due)
                return True

        return False

    except Exception as e:
        print(f"Payment confirmation error: {e}")
        return False

def calculate_days_remaining(user: Dict[str, Any]) -> int:
    subscription_status = user.get('subscription_status', 'trial')

    if subscription_status == 'trial':
        trial_start = user.get('trial_start_date')
        if isinstance(trial_start, str):
            trial_start = datetime.fromisoformat(trial_start.replace('Z', '+00:00'))

        if trial_start:
            trial_end = trial_start + timedelta(days=14)
            remaining = (trial_end - datetime.now()).days
            return max(0, remaining)

    next_due = user.get('next_payment_due')
    if next_due:
        if isinstance(next_due, str):
            next_due = datetime.fromisoformat(next_due.replace('Z', '+00:00'))

        remaining = (next_due - datetime.now()).days
        return max(0, remaining)

    return 0
