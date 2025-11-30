import os
import sys
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail, Email, To, Content
from datetime import datetime

# Get SendGrid API key from environment
sendgrid_key = os.getenv('SENDGRID_API_KEY', 'default_key')

def send_email(to_email, from_email, subject, text_content=None, html_content=None):
    """Send email using SendGrid"""
    if sendgrid_key == 'default_key':
        print(f"Email would be sent to {to_email}: {subject}")
        return True
    
    try:
        sg = SendGridAPIClient(sendgrid_key)

        message = Mail(
            from_email=Email(from_email),
            to_emails=To(to_email),
            subject=subject
        )

        if html_content:
            message.content = Content("text/html", html_content)
        elif text_content:
            message.content = Content("text/plain", text_content)

        response = sg.send(message)
        return True
        
    except Exception as e:
        print(f"SendGrid error: {e}")
        return False

def send_welcome_email(user_email, username):
    """Send welcome email to new user"""
    subject = "Welcome to Omawi Na! 🎵"
    
    html_content = f"""
    <html>
    <body>
        <h2>Welcome to Omawi Na, {username}!</h2>
        
        <p>Thank you for joining Omawi Na, the professional music hub for musicians.</p>
        
        <h3>Your 14-Day Free Trial Has Started!</h3>
        <p>You now have full access to all Omawi Na features:</p>
        <ul>
            <li>🎼 Upload and manage your music collection</li>
            <li>👤 Create your professional musician profile</li>
            <li>🎵 Use our built-in audio player</li>
            <li>🌐 Share your public portfolio</li>
            <li>📊 Track your music analytics</li>
        </ul>
        
        <p><strong>Important:</strong> After your 14-day trial, you'll need to subscribe for 100 NAD quarterly to continue using Omawi Na.</p>
        
        <p>Get started by uploading your first track!</p>
        
        <p>Best regards,<br>The Omawi Na Team</p>
    </body>
    </html>
    """
    
    return send_email(
        user_email,
        "noreply@omawina.app",
        subject,
        html_content=html_content
    )

def send_payment_reminder(user_email, username, days_remaining):
    """Send payment reminder email"""
    subject = f"Omawi Na Payment Reminder - {days_remaining} days remaining"
    
    html_content = f"""
    <html>
    <body>
        <h2>Payment Reminder, {username}</h2>
        
        <p>Your Omawi Na subscription payment is due in {days_remaining} days.</p>
        
        <p><strong>Subscription Details:</strong></p>
        <ul>
            <li>Amount: 100 NAD</li>
            <li>Billing Period: Quarterly (every 3 months)</li>
            <li>Due Date: {days_remaining} days from now</li>
        </ul>
        
        <p>To avoid any interruption to your service, please ensure your payment method is up to date.</p>
        
        <p><a href="https://omawina.app/subscription">Update Payment Method</a></p>
        
        <p>Thank you for being a valued Omawi Na member!</p>
        
        <p>Best regards,<br>The Omawi Na Team</p>
    </body>
    </html>
    """
    
    return send_email(
        user_email,
        "billing@omawina.app",
        subject,
        html_content=html_content
    )

def send_grace_period_warning(user_email, username):
    """Send grace period warning email"""
    subject = "Omawi Na Account: Payment Overdue - 7 Days to Avoid Suspension"
    
    html_content = f"""
    <html>
    <body>
        <h2>Payment Overdue Warning, {username}</h2>
        
        <p><strong style="color: #ff6b6b;">Your Omawi Na subscription payment is overdue.</strong></p>
        
        <p>You have entered a 7-day grace period. During this time, you can still access your account and make the overdue payment.</p>
        
        <p><strong>What happens next:</strong></p>
        <ul>
            <li>✅ Full access continues for the next 7 days</li>
            <li>⚠️ After 7 days, your account will be suspended</li>
            <li>🔒 Suspended accounts cannot upload or stream music</li>
            <li>💾 Your music and profile remain safe</li>
        </ul>
        
        <p><strong>Amount Due: 100 NAD</strong></p>
        
        <p><a href="https://omawina.app/subscription" style="background: #007bff; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px;">Pay Now</a></p>
        
        <p>Questions? Contact us at support@omawina.app</p>
        
        <p>Best regards,<br>The Omawi Na Team</p>
    </body>
    </html>
    """
    
    return send_email(
        user_email,
        "billing@omawina.app",
        subject,
        html_content=html_content
    )

def send_suspension_notification(user_email, username):
    """Send account suspension notification"""
    subject = "Omawi Na Account Suspended - Payment Required"
    
    html_content = f"""
    <html>
    <body>
        <h2>Account Suspended, {username}</h2>
        
        <p><strong style="color: #dc3545;">Your Omawi Na account has been suspended due to overdue payment.</strong></p>
        
        <p><strong>Current Status:</strong></p>
        <ul>
            <li>🚫 Cannot upload new music</li>
            <li>🚫 Cannot stream existing tracks</li>
            <li>💾 Your music and profile data are preserved</li>
            <li>🔄 Immediate reactivation upon payment</li>
        </ul>
        
        <p><strong>To Reactivate Your Account:</strong></p>
        <ol>
            <li>Pay the overdue amount: 100 NAD</li>
            <li>Your account will be immediately reactivated</li>
            <li>Full access to all features will be restored</li>
        </ol>
        
        <p><a href="https://omawina.app/subscription" style="background: #28a745; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px;">Reactivate Account</a></p>
        
        <p>We understand that circumstances can change. If you're experiencing financial difficulties, please contact us at support@omawina.app</p>
        
        <p>Best regards,<br>The Omawi Na Team</p>
    </body>
    </html>
    """
    
    return send_email(
        user_email,
        "billing@omawina.app",
        subject,
        html_content=html_content
    )

def send_payment_confirmation(user_email, username, amount, next_due_date):
    """Send payment confirmation email"""
    subject = "Omawi Na Payment Confirmed - Thank You!"
    
    html_content = f"""
    <html>
    <body>
        <h2>Payment Confirmed, {username}!</h2>
        
        <p>Thank you for your payment. Your Omawi Na subscription has been renewed.</p>
        
        <p><strong>Payment Details:</strong></p>
        <ul>
            <li>Amount Paid: {amount} NAD</li>
            <li>Payment Date: {datetime.now().strftime('%Y-%m-%d')}</li>
            <li>Next Payment Due: {next_due_date.strftime('%Y-%m-%d')}</li>
            <li>Subscription Status: Active</li>
        </ul>
        
        <p>Your account is now active for the next 3 months. Continue creating and sharing your amazing music!</p>
        
        <p><a href="https://omawina.app/dashboard">Go to Dashboard</a></p>
        
        <p>Best regards,<br>The Omawi Na Team</p>
    </body>
    </html>
    """
    
    return send_email(
        user_email,
        "billing@omawina.app",
        subject,
        html_content=html_content
    )
