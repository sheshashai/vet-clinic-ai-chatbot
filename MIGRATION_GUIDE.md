# PostgreSQL (Supabase) Migration Guide

This document provides instructions for migrating your vet clinic AI chatbot from SQLite to PostgreSQL using Supabase.

## Prerequisites

1. **Supabase Account**: Sign up at [supabase.com](https://supabase.com)
2. **Create a new Supabase project**
3. **Get your database credentials**

## Step 1: Set up Supabase Database

### 1.1 Create Tables
1. Go to your Supabase dashboard
2. Navigate to the SQL Editor
3. Run the SQL script from `supabase_schema.sql`

### 1.2 Get Database Credentials
1. Go to Settings > Database
2. Copy your connection string
3. Note down your project URL and API keys

## Step 2: Environment Configuration

### 2.1 Update Environment Variables
Copy `env.example` to `.env` and fill in your actual values:

```bash
# Database Configuration
DATABASE_URL=postgresql://postgres:[YOUR-PASSWORD]@db.[YOUR-PROJECT-REF].supabase.co:5432/postgres
SUPABASE_URL=https://[YOUR-PROJECT-REF].supabase.co
SUPABASE_ANON_KEY=your-anon-key-here
SUPABASE_SERVICE_ROLE_KEY=your-service-role-key-here

# Other existing environment variables...
OPENAI_API_KEY=your-openai-api-key
TWILIO_ACCOUNT_SID=your-twilio-account-sid
TWILIO_AUTH_TOKEN=your-twilio-auth-token
TWILIO_WHATSAPP_NUMBER=whatsapp:+14155238886
ADMIN_WHATSAPP_NUMBER=whatsapp:+1234567890
SECRET_KEY=your-secret-key-here
FLASK_ENV=development
```

## Step 3: Install Dependencies

### 3.1 Install New Dependencies
```bash
pip install -r requirements.txt
```

The new requirements include:
- `psycopg2-binary` - PostgreSQL adapter
- `flask-sqlalchemy` - SQLAlchemy integration
- `sqlalchemy` - SQL toolkit

## Step 4: Data Migration (Optional)

If you have existing SQLite data to migrate:

### 4.1 Export SQLite Data
```bash
# Connect to your existing SQLite database
sqlite3 database.db

# Export users
.headers on
.mode csv
.output users.csv
SELECT * FROM users;

# Export appointments
.output appointments.csv
SELECT * FROM appointments;
.quit
```

### 4.2 Import to Supabase
1. Go to your Supabase dashboard
2. Navigate to Table Editor
3. Select your table (users or appointments)
4. Use the Import CSV feature to upload your data

## Step 5: Test the Migration

### 5.1 Run the Application
```bash
python server.py
```

### 5.2 Test Key Features
1. **Health Check**: Visit `/health` to verify database connectivity
2. **User Registration**: Create a new user account
3. **User Login**: Test authentication
4. **Appointment Booking**: Test the chatbot appointment booking
5. **Admin Dashboard**: Check appointment management

### 5.3 Verify Database Operations
- Check that new appointments are saved to Supabase
- Verify appointment status updates work
- Test WhatsApp notifications

## Step 6: Production Deployment

### 6.1 Environment Variables
Set these environment variables in your production environment:
- `DATABASE_URL`
- `SUPABASE_URL`
- `SUPABASE_ANON_KEY`
- `SUPABASE_SERVICE_ROLE_KEY`
- All other existing environment variables

### 6.2 Security Considerations
1. **Row Level Security**: Enable RLS policies in Supabase (see supabase_schema.sql)
2. **API Keys**: Use service role key for server-side operations
3. **Connection Pooling**: Already configured in the application

## Changes Made

### Database Connection
- ✅ Replaced `sqlite3` with `psycopg2`
- ✅ Added connection pooling
- ✅ Implemented proper error handling

### SQL Queries
- ✅ Changed parameter style from `?` to `%s`
- ✅ Updated `AUTOINCREMENT` to `SERIAL`
- ✅ Modified `lastrowid` to `RETURNING id`
- ✅ Updated date/time handling for PostgreSQL

### Error Handling
- ✅ Replaced `sqlite3.IntegrityError` with `psycopg2.IntegrityError`
- ✅ Added proper transaction rollback
- ✅ Updated health check queries

### Schema Management
- ✅ Removed table creation from application code
- ✅ Schema is now managed by Supabase

## Troubleshooting

### Common Issues

1. **Connection Failed**
   - Check your DATABASE_URL format
   - Verify Supabase project is active
   - Ensure firewall allows connections

2. **Table Not Found**
   - Run the schema SQL in Supabase SQL Editor
   - Check table names are correct (case-sensitive)

3. **Authentication Issues**
   - Verify password in connection string
   - Check API keys are correct

4. **Performance Issues**
   - Monitor connection pool usage
   - Consider upgrading Supabase plan
   - Implement caching for frequently accessed data

### Support
- Supabase Documentation: https://supabase.com/docs
- PostgreSQL Documentation: https://www.postgresql.org/docs/

## Next Steps

Consider implementing these enhancements:
1. **Real-time subscriptions** using Supabase real-time features
2. **File storage** for pet photos using Supabase Storage
3. **Enhanced authentication** using Supabase Auth
4. **Edge functions** for serverless operations
5. **Database functions** for complex queries
