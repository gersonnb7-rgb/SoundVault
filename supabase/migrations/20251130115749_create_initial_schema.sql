/*
  # Create Omawi Na Initial Database Schema

  ## Overview
  This migration creates the complete database schema for Omawi Na, a music hub platform for musicians.
  It includes user management, track storage, payment tracking, and analytics.

  ## New Tables

  ### 1. users
  Stores musician profiles and subscription information.
  - `id` (uuid, primary key) - Unique user identifier
  - `email` (text, unique) - User email address
  - `username` (text, unique) - Public username for portfolio
  - `full_name` (text) - Full name of the musician
  - `bio` (text) - Artist biography
  - `genre` (text) - Primary music genre
  - `profile_image_url` (text) - URL to profile image
  - `social_links` (jsonb) - Social media links
  - `trial_start_date` (timestamptz) - When trial period started
  - `subscription_status` (text) - Current status: trial, active, grace_period, suspended
  - `last_payment_date` (timestamptz) - Date of last successful payment
  - `next_payment_due` (timestamptz) - Date of next payment
  - `created_at` (timestamptz) - Account creation timestamp

  ### 2. tracks
  Stores uploaded music tracks with rich metadata.
  - `id` (uuid, primary key) - Unique track identifier
  - `user_id` (uuid, foreign key) - Reference to users table
  - `title` (text) - Track title
  - `artist` (text) - Artist name
  - `album` (text) - Album name
  - `genre` (text) - Track genre
  - `release_year` (integer) - Release year
  - `producer_credits` (text) - Producer information
  - `featured_artists` (text) - Featured artists
  - `lyrics` (text) - Song lyrics
  - `file_path` (text) - Path to audio file
  - `file_size` (bigint) - File size in bytes
  - `duration_seconds` (integer) - Track duration
  - `cover_art_url` (text) - URL to cover art
  - `play_count` (integer) - Number of plays
  - `created_at` (timestamptz) - Upload timestamp
  - `updated_at` (timestamptz) - Last update timestamp

  ### 3. payments
  Tracks all payment transactions.
  - `id` (uuid, primary key) - Unique payment identifier
  - `user_id` (uuid, foreign key) - Reference to users table
  - `stripe_payment_id` (text) - Stripe payment intent ID
  - `amount` (numeric) - Payment amount
  - `currency` (text) - Currency code (NAD)
  - `status` (text) - Payment status
  - `payment_date` (timestamptz) - When payment was made
  - `subscription_period_start` (timestamptz) - Start of subscription period
  - `subscription_period_end` (timestamptz) - End of subscription period

  ### 4. track_plays
  Analytics table for tracking music plays.
  - `id` (uuid, primary key) - Unique play record identifier
  - `track_id` (uuid, foreign key) - Reference to tracks table
  - `user_id` (uuid, foreign key) - Reference to users table (nullable)
  - `ip_address` (inet) - IP address of listener
  - `user_agent` (text) - Browser user agent
  - `played_at` (timestamptz) - When track was played

  ## Security

  ### Row Level Security (RLS)
  All tables have RLS enabled with appropriate policies:

  #### users table
  - Users can read their own profile
  - Users can update their own profile
  - Public can view basic profile info for portfolio pages

  #### tracks table
  - Users can view all their own tracks
  - Users can insert their own tracks
  - Users can update their own tracks
  - Users can delete their own tracks
  - Public can view tracks for portfolio display

  #### payments table
  - Users can view only their own payment history
  - System can insert payment records

  #### track_plays table
  - Anyone can insert play records (for analytics)
  - Users can view plays for their own tracks

  ## Indexes
  - Users: email, username
  - Tracks: user_id, created_at
  - Payments: user_id, payment_date
  - Track_plays: track_id, played_at
*/

-- Create users table
CREATE TABLE IF NOT EXISTS users (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  email text UNIQUE NOT NULL,
  username text UNIQUE NOT NULL,
  full_name text,
  bio text,
  genre text,
  profile_image_url text,
  social_links jsonb DEFAULT '{}'::jsonb,
  trial_start_date timestamptz DEFAULT now(),
  subscription_status text DEFAULT 'trial',
  last_payment_date timestamptz,
  next_payment_due timestamptz DEFAULT (now() + interval '14 days'),
  created_at timestamptz DEFAULT now()
);

-- Create tracks table
CREATE TABLE IF NOT EXISTS tracks (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id uuid REFERENCES users(id) ON DELETE CASCADE NOT NULL,
  title text NOT NULL,
  artist text NOT NULL,
  album text,
  genre text,
  release_year integer,
  producer_credits text,
  featured_artists text,
  lyrics text,
  file_path text NOT NULL,
  file_size bigint,
  duration_seconds integer,
  cover_art_url text,
  play_count integer DEFAULT 0,
  created_at timestamptz DEFAULT now(),
  updated_at timestamptz DEFAULT now()
);

-- Create payments table
CREATE TABLE IF NOT EXISTS payments (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id uuid REFERENCES users(id) ON DELETE CASCADE NOT NULL,
  stripe_payment_id text,
  amount numeric(10, 2) NOT NULL,
  currency text DEFAULT 'NAD',
  status text NOT NULL,
  payment_date timestamptz DEFAULT now(),
  subscription_period_start timestamptz,
  subscription_period_end timestamptz
);

-- Create track_plays table for analytics
CREATE TABLE IF NOT EXISTS track_plays (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  track_id uuid REFERENCES tracks(id) ON DELETE CASCADE NOT NULL,
  user_id uuid REFERENCES users(id) ON DELETE SET NULL,
  ip_address inet,
  user_agent text,
  played_at timestamptz DEFAULT now()
);

-- Create indexes
CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
CREATE INDEX IF NOT EXISTS idx_users_username ON users(username);
CREATE INDEX IF NOT EXISTS idx_tracks_user_id ON tracks(user_id);
CREATE INDEX IF NOT EXISTS idx_tracks_created_at ON tracks(created_at);
CREATE INDEX IF NOT EXISTS idx_payments_user_id ON payments(user_id);
CREATE INDEX IF NOT EXISTS idx_payments_payment_date ON payments(payment_date);
CREATE INDEX IF NOT EXISTS idx_track_plays_track_id ON track_plays(track_id);
CREATE INDEX IF NOT EXISTS idx_track_plays_played_at ON track_plays(played_at);

-- Enable Row Level Security
ALTER TABLE users ENABLE ROW LEVEL SECURITY;
ALTER TABLE tracks ENABLE ROW LEVEL SECURITY;
ALTER TABLE payments ENABLE ROW LEVEL SECURITY;
ALTER TABLE track_plays ENABLE ROW LEVEL SECURITY;

-- RLS Policies for users table
CREATE POLICY "Users can view own profile"
  ON users FOR SELECT
  TO authenticated
  USING (id = auth.uid()::uuid);

CREATE POLICY "Users can update own profile"
  ON users FOR UPDATE
  TO authenticated
  USING (id = auth.uid()::uuid)
  WITH CHECK (id = auth.uid()::uuid);

CREATE POLICY "Public can view basic profile info"
  ON users FOR SELECT
  TO anon
  USING (true);

-- RLS Policies for tracks table
CREATE POLICY "Users can view own tracks"
  ON tracks FOR SELECT
  TO authenticated
  USING (user_id = auth.uid()::uuid);

CREATE POLICY "Users can insert own tracks"
  ON tracks FOR INSERT
  TO authenticated
  WITH CHECK (user_id = auth.uid()::uuid);

CREATE POLICY "Users can update own tracks"
  ON tracks FOR UPDATE
  TO authenticated
  USING (user_id = auth.uid()::uuid)
  WITH CHECK (user_id = auth.uid()::uuid);

CREATE POLICY "Users can delete own tracks"
  ON tracks FOR DELETE
  TO authenticated
  USING (user_id = auth.uid()::uuid);

CREATE POLICY "Public can view tracks for portfolio"
  ON tracks FOR SELECT
  TO anon
  USING (true);

-- RLS Policies for payments table
CREATE POLICY "Users can view own payments"
  ON payments FOR SELECT
  TO authenticated
  USING (user_id = auth.uid()::uuid);

-- RLS Policies for track_plays table
CREATE POLICY "Anyone can insert play records"
  ON track_plays FOR INSERT
  TO anon, authenticated
  WITH CHECK (true);

CREATE POLICY "Users can view plays for own tracks"
  ON track_plays FOR SELECT
  TO authenticated
  USING (
    EXISTS (
      SELECT 1 FROM tracks
      WHERE tracks.id = track_plays.track_id
      AND tracks.user_id = auth.uid()::uuid
    )
  );