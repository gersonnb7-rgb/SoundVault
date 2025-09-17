import stripe
import os
from datetime import datetime, timedelta
from database import update_subscription_status, get_user_by_id

# Initialize Stripe
stripe.api_key = os.getenv('STRIPE_SECRET_KEY', 'sk_test_default_key')

def check_subscription_status(user_id):
    """Check and update subscription status based on payment dates"""
    user = get_user_by_id(user_id)
    if not user:
        return 'unknown'
    
    now = datetime.now()
    trial_start = user['trial_start_date']
    next_payment_due = user['next_payment_due']
    current_status = user['subscription_status']
    
    # Check if still in trial period
    if current_status == 'trial':
        trial_end = trial_start + timedelta(days=14)
        if now < trial_end:
            return 'trial'
        else:
            # Trial ended, check if payment was made
            if user['last_payment_date']:
                return 'active'
            else:
                # Start grace period
                grace_end = trial_end + timedelta(days=7)
                update_subscription_status(user_id, 'grace_period')
                return 'grace_period'
    
    # Check if payment is overdue
    if next_payment_due and now > next_payment_due:
        if current_status == 'active':
            # Start grace period
            update_subscription_status(user_id, 'grace_period')
            return 'grace_period'
        elif current_status == 'grace_period':
            # Check if grace period expired
            grace_end = next_payment_due + timedelta(days=7)
            if now > grace_end:
                update_subscription_status(user_id, 'suspended')
                return 'suspended'
            return 'grace_period'
    
    return current_status

def create_payment_intent(user_id, amount_nad=100):
    """Create Stripe payment intent for subscription"""
    try:
        # Convert NAD to cents (Stripe uses smallest currency unit)
        amount_cents = int(amount_nad * 100)
        
        intent = stripe.PaymentIntent.create(
            amount=amount_cents,
            currency='nad',  # Namibian Dollar
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

def confirm_payment(payment_intent_id, user_id):
    """Confirm payment and update subscription"""
    try:
        intent = stripe.PaymentIntent.retrieve(payment_intent_id)
        
        if intent.status == 'succeeded':
            # Update subscription status
            now = datetime.now()
            next_due = now + timedelta(days=90)  # 3 months
            
            success = update_subscription_status(
                user_id, 
                'active', 
                payment_date=now, 
                next_due_date=next_due
            )
            
            if success:
                # Record payment in database
                record_payment(user_id, intent.id, intent.amount / 100, 'succeeded', now, next_due)
                return True
        
        return False
        
    except Exception as e:
        print(f"Payment confirmation error: {e}")
        return False

def record_payment(user_id, stripe_payment_id, amount, status, payment_date, period_end):
    """Record payment in database"""
    from database import get_db_connection
    
    conn = get_db_connection()
    if not conn:
        return False
    
    cur = None
    try:
        cur = conn.cursor()
        
        cur.execute("""
            INSERT INTO payments (user_id, stripe_payment_id, amount, status, 
                                payment_date, subscription_period_start, subscription_period_end)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, (user_id, stripe_payment_id, amount, status, payment_date, payment_date, period_end))
        
        conn.commit()
        cur.close()
        conn.close()
        return True
        
    except Exception as e:
        print(f"Error recording payment: {e}")
        conn.rollback()
        if cur:
            cur.close()
        conn.close()
        return False

def get_payment_history(user_id):
    """Get payment history for user"""
    from database import get_db_connection
    
    conn = get_db_connection()
    if not conn:
        return []
    
    cur = None
    try:
        cur = conn.cursor()
        cur.execute("""
            SELECT stripe_payment_id, amount, currency, status, payment_date,
                   subscription_period_start, subscription_period_end
            FROM payments 
            WHERE user_id = %s 
            ORDER BY payment_date DESC
        """, (user_id,))
        
        payments = cur.fetchall()
        cur.close()
        conn.close()
        
        return [{
            'stripe_payment_id': payment[0],
            'amount': payment[1],
            'currency': payment[2],
            'status': payment[3],
            'payment_date': payment[4],
            'period_start': payment[5],
            'period_end': payment[6]
        } for payment in payments]
        
    except Exception as e:
        print(f"Error getting payment history: {e}")
        if cur:
            cur.close()
        conn.close()
        return []

def calculate_days_remaining(user):
    """Calculate days remaining in current subscription period"""
    if user['subscription_status'] == 'trial':
        trial_end = user['trial_start_date'] + timedelta(days=14)
        remaining = (trial_end - datetime.now()).days
        return max(0, remaining)
    
    if user['next_payment_due']:
        remaining = (user['next_payment_due'] - datetime.now()).days
        return max(0, remaining)
    
    return 0
