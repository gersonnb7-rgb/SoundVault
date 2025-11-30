import streamlit as st
from datetime import datetime, timedelta
from auth import require_auth
from payment import (
    check_subscription_status, 
    calculate_days_remaining, 
    create_payment_intent,
    get_payment_history
)

st.set_page_config(
    page_title="Subscription - Omawi Na",
    page_icon="💳",
    layout="wide"
)

# Require authentication
user = require_auth()

# Check subscription status
subscription_status = check_subscription_status(user['id'])
days_remaining = calculate_days_remaining(user)

st.title("💳 Subscription Management")

# Current status section
st.subheader("📊 Current Status")

if subscription_status == 'trial':
    st.info(f"🆓 **Free Trial Active** - {days_remaining} days remaining")
    st.progress((14 - days_remaining) / 14)
    
elif subscription_status == 'active':
    st.success(f"✅ **Subscription Active** - {days_remaining} days until next payment")
    next_payment = user.get('next_payment_due')
    if next_payment:
        st.info(f"Next payment due: {next_payment.strftime('%Y-%m-%d')}")
    
elif subscription_status == 'grace_period':
    st.warning(f"⚠️ **Grace Period** - Payment overdue, {7 - (datetime.now() - user['next_payment_due']).days} days remaining")
    
elif subscription_status == 'suspended':
    st.error("🚫 **Account Suspended** - Payment required to reactivate")

# Subscription details
st.markdown("---")
st.subheader("💰 Subscription Details")

col1, col2 = st.columns(2)

with col1:
    st.markdown("""
    **Omawi Na Pro Subscription**
    
    ✅ Unlimited music uploads
    ✅ Professional portfolio page
    ✅ Built-in audio player
    ✅ Track analytics
    ✅ Private sharing links
    ✅ Email support
    
    **Price:** 100 NAD every 3 months
    """)

with col2:
    st.markdown("""
    **What's Included:**
    
    🎵 High-quality audio support (MP3, WAV, FLAC)
    📊 Detailed play statistics
    🌐 Shareable artist portfolio
    🔒 Password-protected private links
    📧 Email notifications
    💾 Secure cloud storage
    """)

# Payment section
st.markdown("---")
st.subheader("💳 Payment Management")

if subscription_status in ['trial', 'grace_period', 'suspended']:
    st.markdown("### Make Payment")
    
    if subscription_status == 'trial':
        st.info("Your free trial is ending soon. Subscribe now to continue using Omawi Na!")
    elif subscription_status == 'grace_period':
        st.warning("Your payment is overdue. Please pay now to avoid account suspension.")
    else:
        st.error("Your account is suspended. Pay now to reactivate immediately.")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("""
        **Payment Amount:** 100 NAD (Namibian Dollars)
        **Billing Period:** Quarterly (every 3 months)
        **Payment Method:** Secure Stripe payment processing
        """)
    
    with col2:
        if st.button("💳 Pay 100 NAD", type="primary", use_container_width=True):
            with st.spinner("Setting up payment..."):
                payment_intent = create_payment_intent(user['id'], 100)
                
                if payment_intent:
                    st.success("Payment setup successful!")
                    st.info("In a real implementation, this would redirect to Stripe checkout.")
                    
                    # Simulate successful payment for demo
                    st.markdown("""
                    **Demo Mode:** Payment would be processed via Stripe.
                    
                    After successful payment:
                    - Account immediately reactivated
                    - Next payment due in 3 months
                    - Confirmation email sent
                    """)
                    
                    if st.button("✅ Simulate Successful Payment"):
                        # In real implementation, this would be handled by Stripe webhook
                        from payment import confirm_payment
                        if confirm_payment(payment_intent['payment_intent_id'], user['id']):
                            st.success("Payment confirmed! Account reactivated.")
                            st.balloons()
                            st.rerun()
                else:
                    st.error("Failed to setup payment. Please try again.")

else:
    st.success("✅ Your subscription is active!")
    
    # Auto-renewal info
    next_payment = user.get('next_payment_due')
    if next_payment:
        st.info(f"Your subscription will auto-renew on {next_payment.strftime('%Y-%m-%d')} for 100 NAD.")
    
    # Cancel subscription (placeholder)
    with st.expander("⚙️ Subscription Settings"):
        st.markdown("**Manage Your Subscription**")
        
        st.warning("⚠️ Canceling your subscription will:")
        st.markdown("""
        - Stop automatic renewals
        - Keep your account active until the current period ends
        - Preserve all your music and data
        - Allow reactivation at any time
        """)
        
        if st.button("❌ Cancel Auto-Renewal", type="secondary"):
            st.info("Subscription cancellation would be processed here.")

# Payment history
st.markdown("---")
st.subheader("📄 Payment History")

payment_history = get_payment_history(user['id'])

if payment_history:
    for payment in payment_history:
        with st.container():
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.markdown(f"**{payment['payment_date'].strftime('%Y-%m-%d')}**")
            
            with col2:
                st.markdown(f"**{payment['amount']} {payment['currency'].upper()}**")
            
            with col3:
                status_color = "🟢" if payment['status'] == 'succeeded' else "🔴"
                st.markdown(f"{status_color} {payment['status'].title()}")
            
            with col4:
                if payment['period_end']:
                    st.markdown(f"Valid until {payment['period_end'].strftime('%Y-%m-%d')}")
            
            st.markdown("---")
else:
    st.info("No payment history available.")

# Billing information
st.markdown("---")
st.subheader("📧 Billing Information")

col1, col2 = st.columns(2)

with col1:
    st.markdown(f"""
    **Account:** {user['email']}
    **Username:** {user['username']}
    **Account Created:** {user['created_at'].strftime('%Y-%m-%d')}
    """)

with col2:
    st.markdown("""
    **Currency:** NAD (Namibian Dollars)
    **Payment Processor:** Stripe
    **Support:** support@soundvault.app
    """)

# FAQ
with st.expander("❓ Frequently Asked Questions"):
    st.markdown("""
    **Q: Can I cancel my subscription at any time?**
    A: Yes, you can cancel auto-renewal at any time. Your account remains active until the current period ends.
    
    **Q: What happens if I miss a payment?**
    A: You get a 7-day grace period to make the payment. After that, your account is suspended but not deleted.
    
    **Q: How do I reactivate a suspended account?**
    A: Simply make the overdue payment and your account will be immediately reactivated.
    
    **Q: Is my music safe if I cancel?**
    A: Yes, all your music and data are preserved. You can reactivate at any time.
    
    **Q: Do you offer refunds?**
    A: Please contact support@soundvault.app for refund requests.
    """)
