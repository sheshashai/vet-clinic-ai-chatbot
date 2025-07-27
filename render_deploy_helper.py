#!/usr/bin/env python3
"""
Render Deploy Trigger Script
This script creates a deploy hook URL that you can use to trigger deployments
"""
import requests
import json
import os
from dotenv import load_dotenv

def create_deploy_hook():
    """Instructions for creating and using Render deploy hooks"""
    
    print("🔗 RENDER.COM DEPLOY HOOK SETUP")
    print("=" * 35)
    
    print("\n📋 STEPS TO CREATE DEPLOY HOOK:")
    print("1. Go to your Render service dashboard")
    print("2. Click 'Settings' in the left sidebar")
    print("3. Scroll down to 'Deploy Hook'")
    print("4. Click 'Create Deploy Hook'")
    print("5. Copy the webhook URL")
    
    print("\n🚀 MANUAL DEPLOYMENT COMMANDS:")
    print("After you get the deploy hook URL, you can use:")
    print("curl -X POST 'https://api.render.com/deploy/srv-XXXXXX?key=YYYYYY'")
    print("Or use the PowerShell equivalent:")
    print("Invoke-RestMethod -Uri 'https://api.render.com/deploy/srv-XXXXXX?key=YYYYYY' -Method POST")
    
    print("\n🛠️ TROUBLESHOOTING EXISTING SERVICE:")
    print("If you have an existing service that's not working:")
    print("1. Go to your service dashboard")
    print("2. Check 'Environment' - ensure ALL variables are set")
    print("3. Check 'Logs' for specific error messages")
    print("4. Try 'Manual Deploy' → 'Deploy latest commit'")
    print("5. Monitor the build process in real-time")
    
    print("\n📊 SERVICE CONFIGURATION CHECK:")
    print("Verify these settings in your Render service:")
    print("- Build Command: pip install -r requirements.txt")
    print("- Start Command: python -m gunicorn server:app -c gunicorn.conf.py")
    print("- Runtime: Python 3")
    print("- Environment: Production")
    
    return True

def check_github_status():
    """Check if GitHub repository is accessible"""
    repo_url = "https://api.github.com/repos/sheshashai/vet-clinic-ai-chatbot"
    
    try:
        response = requests.get(repo_url, timeout=10)
        if response.status_code == 200:
            repo_data = response.json()
            print(f"✅ GitHub repository accessible")
            print(f"   - Default branch: {repo_data.get('default_branch', 'main')}")
            print(f"   - Last updated: {repo_data.get('updated_at', 'Unknown')}")
            print(f"   - Private: {repo_data.get('private', False)}")
            return True
        else:
            print(f"⚠️  GitHub repository status: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error checking GitHub: {e}")
        return False

def main():
    print("🚀 RENDER.COM DEPLOYMENT ASSISTANT")
    print("=" * 40)
    
    # Check GitHub repository status
    print("\n🔍 CHECKING GITHUB REPOSITORY:")
    github_ok = check_github_status()
    
    # Check local environment
    print("\n🔍 CHECKING LOCAL ENVIRONMENT:")
    load_dotenv()
    
    required_vars = [
        'DATABASE_URL', 'SUPABASE_URL', 'OPENAI_API_KEY', 
        'TWILIO_ACCOUNT_SID', 'SECRET_KEY'
    ]
    
    env_ok = True
    for var in required_vars:
        if os.getenv(var):
            print(f"✅ {var}: Set")
        else:
            print(f"❌ {var}: Missing")
            env_ok = False
    
    # Provide deployment instructions
    print("\n" + "=" * 40)
    if github_ok and env_ok:
        print("✅ READY FOR DEPLOYMENT")
        create_deploy_hook()
        
        print("\n🎯 NEXT STEPS:")
        print("1. Follow the manual deployment steps above")
        print("2. Use the environment variables from deploy_to_render.py output")
        print("3. Monitor deployment in Render dashboard")
        print("4. Test endpoints after deployment completes")
        
    else:
        print("❌ ISSUES DETECTED - Fix these before deploying:")
        if not github_ok:
            print("   - GitHub repository access issues")
        if not env_ok:
            print("   - Missing environment variables")

if __name__ == "__main__":
    main()
