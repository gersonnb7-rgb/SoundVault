# Omawi Na - Deployment Guide

## Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

Or using the pyproject.toml:
```bash
pip install mutagen supabase sendgrid streamlit stripe
```

### 2. Environment Setup

Ensure your `.env` file has the following variables:

```env
SUPABASE_URL=your_supabase_project_url
SUPABASE_ANON_KEY=your_supabase_anon_key
STRIPE_SECRET_KEY=your_stripe_secret_key
SENDGRID_API_KEY=your_sendgrid_api_key
```

### 3. Database Setup

The database schema is already applied to your Supabase project. You can verify by checking:
- Tables: users, tracks, payments, track_plays
- RLS is enabled on all tables
- Proper indexes are created

### 4. Run the Application

```bash
streamlit run app.py --server.port 5000
```

Or on Replit, it will start automatically.

## Testing the Application

### Demo Mode Access

To test without full authentication, access the app with query parameters:

```
http://your-app-url/?demo_user_email=test@example.com&demo_user_name=testuser
```

This will automatically create a test user and log them in.

### Feature Testing Checklist

- [ ] User registration (auto-created on first login)
- [ ] Profile creation and editing
- [ ] Music file upload (MP3, WAV, FLAC)
- [ ] Track metadata extraction
- [ ] Audio playback
- [ ] Portfolio page viewing
- [ ] Subscription status checking
- [ ] Payment flow (requires Stripe configuration)

## Application Structure

```
omawi-na/
├── app.py                 # Main application entry point
├── auth.py                # Authentication handling
├── database.py            # Database operations (Supabase)
├── supabase_client.py     # Supabase client singleton
├── payment.py             # Stripe payment integration
├── email_service.py       # SendGrid email notifications
├── audio_utils.py         # Audio file processing utilities
├── pages/
│   ├── 1_Dashboard.py     # User dashboard
│   ├── 2_Upload_Music.py  # Music upload interface
│   ├── 3_Profile.py       # Profile management
│   ├── 4_Subscription.py  # Subscription management
│   └── 5_Portfolio.py     # Public portfolio display
├── .env                   # Environment variables
├── pyproject.toml         # Project dependencies
├── requirements.txt       # Pip requirements
└── IMPROVEMENTS.md        # Detailed improvements documentation
```

## Database Schema

### Key Tables

1. **users** - Stores user profiles and subscription status
2. **tracks** - Music files with metadata
3. **payments** - Payment transaction history
4. **track_plays** - Analytics for tracking plays

All tables use UUID primary keys and have Row Level Security enabled.

## Security Features

### Row Level Security (RLS)

All database tables have RLS policies that ensure:
- Users can only access their own data
- Public can view portfolio information
- Payment information is strictly private
- Analytics data is properly scoped

### Authentication

Currently supports:
- Session-based demo authentication
- Ready for Replit Auth integration
- Email-based user lookup

## API Integrations

### Supabase
- Database operations
- Real-time capabilities (ready)
- File storage (ready for implementation)

### Stripe
- Payment intent creation
- Subscription management
- Quarterly billing (100 NAD)

### SendGrid
- Welcome emails
- Payment reminders
- Suspension notifications

## Subscription Flow

1. **Trial Period** (14 days)
   - Full access to all features
   - Automatic upon signup

2. **Active Subscription**
   - 100 NAD quarterly payment
   - Full feature access
   - Automatic renewal

3. **Grace Period** (7 days)
   - Payment overdue
   - Limited warnings
   - Full access maintained

4. **Suspended**
   - After grace period expires
   - Cannot upload or stream
   - Data preserved
   - Instant reactivation on payment

## File Storage

### Current Implementation
- Local file system storage in `uploads/` directory
- Organized by user_id
- Named by track_id

### Future Enhancement
Consider migrating to Supabase Storage for:
- Better scalability
- CDN delivery
- Automatic backups
- Direct URL access

## Performance Considerations

### Database Indexes
- Email and username for users
- User_id and created_at for tracks
- User_id and payment_date for payments
- Track_id and played_at for analytics

### Query Optimization
- Use of `maybeSingle()` for single record queries
- Efficient ordering with indexed columns
- Proper foreign key relationships

## Monitoring & Maintenance

### Database Health
Check table row counts:
```sql
SELECT 'users' as table_name, COUNT(*) FROM users
UNION ALL
SELECT 'tracks', COUNT(*) FROM tracks
UNION ALL
SELECT 'payments', COUNT(*) FROM payments;
```

### Subscription Status Check
Monitor users in different states:
```sql
SELECT subscription_status, COUNT(*)
FROM users
GROUP BY subscription_status;
```

### Storage Usage
Track file storage:
```sql
SELECT
  COUNT(*) as total_tracks,
  SUM(file_size) / (1024*1024*1024) as storage_gb
FROM tracks;
```

## Troubleshooting

### Common Issues

1. **Supabase Connection Error**
   - Verify SUPABASE_URL and SUPABASE_ANON_KEY in .env
   - Check network connectivity
   - Verify Supabase project is active

2. **File Upload Fails**
   - Check uploads/ directory permissions
   - Verify file size limits (50MB max)
   - Check supported formats (MP3, WAV, FLAC)

3. **Payment Processing Issues**
   - Verify Stripe API key configuration
   - Check currency support (NAD)
   - Test with Stripe test mode first

4. **Email Not Sending**
   - Verify SendGrid API key
   - Check email sender verification
   - Review SendGrid dashboard for errors

## Production Deployment Checklist

- [ ] Set production Supabase credentials
- [ ] Configure production Stripe keys
- [ ] Set up SendGrid sender verification
- [ ] Enable HTTPS
- [ ] Configure proper CORS settings
- [ ] Set up database backups
- [ ] Configure file storage limits
- [ ] Set up monitoring and logging
- [ ] Test payment flow end-to-end
- [ ] Configure email templates
- [ ] Set up error tracking
- [ ] Configure rate limiting

## Support & Documentation

For detailed code improvements, see `IMPROVEMENTS.md`

For project overview, see `replit.md`

## Next Steps

1. Install dependencies
2. Configure environment variables
3. Test with demo mode
4. Configure Stripe for payments
5. Set up SendGrid for emails
6. Deploy to production
7. Monitor and iterate
