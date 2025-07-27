#!/usr/bin/env python3
"""
Debug script for Render.com deployment
Run this to check if environment variables are properly loaded
"""
import os
from dotenv import load_dotenv

print("🔍 RENDER.COM DEPLOYMENT DEBUG")
print("=" * 50)

# Try to load .env (won't work on Render, but good for local testing)
try:
    load_dotenv()
    print("✅ .env file loaded (local environment)")
except:
    print("⚠️  No .env file (expected on Render.com)")

print("\n📋 ENVIRONMENT VARIABLES CHECK:")
print("-" * 30)

required_vars = [
    'DATABASE_URL',
    'SUPABASE_URL', 
    'SUPABASE_ANON_KEY',
    'SUPABASE_SERVICE_ROLE_KEY',
    'OPENAI_API_KEY',
    'TWILIO_ACCOUNT_SID',
    'TWILIO_AUTH_TOKEN',
    'TWILIO_WHATSAPP_NUMBER',
    'ADMIN_WHATSAPP_NUMBER',
    'SECRET_KEY',
    'FLASK_ENV'
]

missing_vars = []
for var in required_vars:
    value = os.getenv(var)
    if value:
        # Show partial value for security
        if len(value) > 20:
            display_value = value[:10] + "..." + value[-5:]
        else:
            display_value = value[:5] + "..." if len(value) > 5 else value
        print(f"✅ {var}: {display_value}")
    else:
        print(f"❌ {var}: NOT SET")
        missing_vars.append(var)

print(f"\n📊 SUMMARY:")
print(f"Total variables: {len(required_vars)}")
print(f"Set correctly: {len(required_vars) - len(missing_vars)}")
print(f"Missing: {len(missing_vars)}")

if missing_vars:
    print(f"\n🚨 MISSING VARIABLES:")
    for var in missing_vars:
        print(f"   - {var}")
    print(f"\n💡 ACTION REQUIRED:")
    print(f"   Go to Render.com dashboard > Environment")
    print(f"   Add the missing environment variables")
    print(f"   Redeploy your service")
else:
    print(f"\n🎉 All environment variables are set!")
    
    # Test database connection if all vars are present
    print(f"\n🔗 TESTING DATABASE CONNECTION:")
    try:
        import psycopg2
        from psycopg2.extras import RealDictCursor
        
        conn = psycopg2.connect(os.getenv('DATABASE_URL'))
        conn.cursor_factory = RealDictCursor
        
        with conn.cursor() as cur:
            cur.execute("SELECT 1")
            cur.fetchone()
        
        conn.close()
        print("✅ Database connection successful!")
        
    except Exception as e:
        print(f"❌ Database connection failed: {e}")

print(f"\n🌐 DEPLOYMENT PLATFORM:")
if os.getenv('RENDER'):
    print("✅ Running on Render.com")
elif os.getenv('PORT'):
    print("⚠️  Running on cloud platform (possibly Render)")
else:
    print("🏠 Running locally")

print(f"\n" + "=" * 50)
