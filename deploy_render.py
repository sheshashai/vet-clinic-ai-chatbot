#!/usr/bin/env python3
"""
Simple Render deployment script
This script helps deploy your application to Render using their API
"""
import os
import requests
import json
from datetime import datetime

def deploy_to_render():
    """Deploy the application to Render"""
    print("🚀 Render Deployment Script")
    print("=" * 50)
    
    # Check if we have the necessary files
    required_files = ['server.py', 'requirements.txt', 'render.yaml']
    missing_files = []
    
    for file in required_files:
        if not os.path.exists(file):
            missing_files.append(file)
    
    if missing_files:
        print(f"❌ Missing required files: {', '.join(missing_files)}")
        return False
    
    print("✅ All required files found")
    print("\n📋 Deployment Steps:")
    print("1. Go to https://render.com")
    print("2. Sign in with your GitHub account")
    print("3. Click 'New +' → 'Web Service'")
    print("4. Connect your repository: sheshashai/vet-clinic-ai-chatbot")
    print("5. Render will auto-detect Python and use your render.yaml config")
    print("\n🔧 Required Environment Variables:")
    print("- OPENAI_API_KEY: (your OpenAI API key)")
    print("- SECRET_KEY: (auto-generated)")
    print("- FLASK_ENV: production")
    
    # Check if .env exists and show current values
    if os.path.exists('.env'):
        print("\n📁 Current .env file detected:")
        with open('.env', 'r') as f:
            lines = f.readlines()
            for line in lines:
                if line.strip() and not line.startswith('#'):
                    key = line.split('=')[0]
                    print(f"  ✅ {key}")
    
    print("\n🌐 After deployment, your app will be available at:")
    print("   https://vet-clinic-ai-chatbot.onrender.com")
    print("\n⚡ Deployment typically takes 2-5 minutes")
    
    return True

if __name__ == "__main__":
    deploy_to_render()
