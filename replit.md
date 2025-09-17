# Overview

SoundVault is a subscription-based music hub designed exclusively for musicians to store, manage, and showcase their music catalog. It serves as a private, professional vault and portfolio platform where artists can upload high-quality audio files, create public portfolios, and manage their music business. The application features a 14-day free trial followed by a quarterly subscription model (100 NAD every 3 months) with integrated payment processing and account status management.

# User Preferences

Preferred communication style: Simple, everyday language.

# System Architecture

## Frontend Architecture
- **Framework**: Streamlit-based web application with multi-page architecture
- **Layout**: Wide layout configuration optimized for music management interfaces
- **Navigation**: Page-based routing system with dedicated sections for Dashboard, Upload, Profile, Subscription, and Portfolio
- **UI Components**: Streamlit native components including file uploaders, audio players, forms, and metrics displays

## Backend Architecture
- **Database Layer**: PostgreSQL with psycopg2 connector for data persistence
- **Authentication System**: Custom session-based authentication with user management
- **File Management**: Audio file upload and metadata extraction using Mutagen library
- **Business Logic**: Subscription status tracking with trial, active, grace period, and suspended states

## Data Models
- **Users Table**: Stores user profiles, subscription status, payment dates, and trial information
- **Tracks Table**: Manages uploaded music files with metadata, play counts, and file paths
- **Subscription Management**: Trial period tracking, payment due dates, and account status transitions

## Payment Processing
- **Payment Gateway**: Stripe integration for handling quarterly subscriptions
- **Currency**: Namibian Dollars (NAD) with 100 NAD quarterly billing
- **Subscription States**: Trial (14 days) → Active → Grace Period (7 days) → Suspended
- **Reactivation Flow**: Automatic account restoration upon payment

## File Storage & Processing
- **Audio Support**: MP3, WAV, and FLAC file formats
- **Metadata Extraction**: Automatic extraction of title, artist, album, genre, year, and duration
- **File Validation**: Size limits and format verification before upload

## User Experience Flow
- **Onboarding**: 14-day free trial with immediate access to all features
- **Dashboard**: Central hub for track management, statistics, and subscription status
- **Portfolio**: Public-facing artist pages with shareable links
- **Upload System**: Drag-and-drop interface with automatic metadata detection

# External Dependencies

## Core Services
- **PostgreSQL Database**: Primary data storage for users, tracks, and subscription information
- **Stripe Payment Gateway**: Quarterly subscription processing and payment management
- **SendGrid Email Service**: Automated email notifications for welcome, reminders, and billing

## Python Libraries
- **Streamlit**: Web application framework for the entire frontend
- **psycopg2**: PostgreSQL database connectivity
- **Mutagen**: Audio file metadata extraction and processing
- **Stripe Python SDK**: Payment processing integration
- **SendGrid Python SDK**: Email service integration

## Environment Configuration
- Database credentials (PGHOST, PGDATABASE, PGUSER, PGPASSWORD, PGPORT)
- Stripe API keys for payment processing
- SendGrid API key for email notifications

## File Processing
- Audio file validation and metadata extraction capabilities
- Support for multiple audio formats with quality preservation
- File size limitations and storage management