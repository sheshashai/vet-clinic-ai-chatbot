#!/usr/bin/env python3
"""
Render.com Deployment Helper Script
This script helps create and configure a Render.com service
"""
import json
import os
from datetime import datetime

def create_render_config():
    """Create a comprehensive render configuration"""
    
    # Load environment variables from .env
    env_vars = {}
    try:
        with open('.env', 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    env_vars[key.strip()] = value.strip()
    except FileNotFoundError:
        print("⚠️  .env file not found")
    
    # Required environment variables for Render
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
        'SECRET_KEY'
    ]
    
    print("🔧 RENDER.COM DEPLOYMENT CONFIGURATION")
    print("=" * 50)
    
    print("\n📋 ENVIRONMENT VARIABLES STATUS:")
    missing_vars = []
    for var in required_vars:
        if var in env_vars:
            value = env_vars[var]
            display_value = value[:10] + "..." + value[-5:] if len(value) > 20 else value
            print(f"✅ {var}: {display_value}")
        else:
            print(f"❌ {var}: MISSING")
            missing_vars.append(var)
    
    if missing_vars:
        print(f"\n🚨 Missing variables: {', '.join(missing_vars)}")
        return False
    
    # Generate deployment instructions
    print(f"\n🚀 RENDER.COM DEPLOYMENT STEPS:")
    print("-" * 30)
    
    print("1. Go to https://render.com and sign in")
    print("2. Click 'New +' → 'Web Service'")
    print("3. Connect your GitHub repository: sheshashai/vet-clinic-ai-chatbot")
    print("4. Configure service settings:")
    print("   - Name: vet-clinic-ai-chatbot")
    print("   - Runtime: Python 3")
    print("   - Build Command: pip install -r requirements.txt")
    print("   - Start Command: python -m gunicorn server:app -c gunicorn.conf.py")
    print("   - Plan: Free")
    
    print("\n5. Add environment variables (copy exact values from .env):")
    for var in required_vars:
        if var in env_vars:
            print(f"   {var}={env_vars[var]}")
    print("   FLASK_ENV=production")
    
    print("\n6. Click 'Create Web Service'")
    print("7. Wait for deployment to complete")
    print("8. Test endpoints:")
    print("   - Health: https://your-app.onrender.com/health")
    print("   - Debug: https://your-app.onrender.com/debug")
    print("   - Main: https://your-app.onrender.com")
    
    # Create a deployment checklist file
    checklist = {
        "deployment_date": datetime.now().isoformat(),
        "repository": "sheshashai/vet-clinic-ai-chatbot",
        "runtime": "Python 3",
        "build_command": "pip install -r requirements.txt",
        "start_command": "python -m gunicorn server:app -c gunicorn.conf.py",
        "environment_variables": {var: "SET" for var in required_vars if var in env_vars},
        "missing_variables": missing_vars,
        "test_endpoints": [
            "https://your-app.onrender.com/health",
            "https://your-app.onrender.com/debug", 
            "https://your-app.onrender.com"
        ]
    }
    
    with open('render_deployment_checklist.json', 'w') as f:
        json.dump(checklist, f, indent=2)
    
    print(f"\n📄 Deployment checklist saved to: render_deployment_checklist.json")
    return True

def test_local_setup():
    """Test if local setup is working correctly"""
    print("\n🧪 TESTING LOCAL SETUP:")
    print("-" * 25)
    
    try:
        # Test database connection
        import psycopg2
        from dotenv import load_dotenv
        
        load_dotenv()
        DATABASE_URL = os.getenv('DATABASE_URL')
        
        if DATABASE_URL:
            conn = psycopg2.connect(DATABASE_URL)
            with conn.cursor() as cur:
                cur.execute("SELECT 1")
                cur.fetchone()
            conn.close()
            print("✅ Database connection successful")
        else:
            print("❌ DATABASE_URL not found")
            return False
        
        # Test OpenAI API key
        OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
        if OPENAI_API_KEY and OPENAI_API_KEY.startswith('sk-'):
            print("✅ OpenAI API key format valid")
        else:
            print("❌ OpenAI API key invalid or missing")
            return False
        
        print("✅ Local setup is ready for deployment")
        return True
        
    except Exception as e:
        print(f"❌ Local setup error: {e}")
        return False

if __name__ == "__main__":
    print("🚀 RENDER.COM DEPLOYMENT HELPER")
    print("=" * 35)
    
    # Test local setup first
    if test_local_setup():
        # Create deployment configuration
        if create_render_config():
            print(f"\n🎉 Ready for Render.com deployment!")
            print(f"📋 Follow the steps above to deploy your service")
        else:
            print(f"\n❌ Please fix missing environment variables first")
    else:
        print(f"\n❌ Local setup issues detected. Fix these before deploying.")
