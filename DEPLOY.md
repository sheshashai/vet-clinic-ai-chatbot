# 🚀 Render Deployment Guide

## Quick Deploy (Recommended)

### Option 1: Web Interface (Easiest)
1. Go to [render.com](https://render.com)
2. Sign up/Login with GitHub
3. Click "New +" → "Web Service"
4. Connect repository: `sheshashai/vet-clinic-ai-chatbot`
5. Render auto-detects Python Flask app
6. Click "Deploy"

### Option 2: Using render.yaml (Auto-deploy)
1. Commit the `render.yaml` file to your repo
2. In Render dashboard, select "Deploy from Repository"
3. Choose your repo - Render will use the yaml config

## Required Environment Variables
Set these in Render Dashboard → Environment:

```
OPENAI_API_KEY=your_openai_api_key_here
SECRET_KEY=any_random_secret_string
TWILIO_ACCOUNT_SID=your_twilio_sid (optional)
TWILIO_AUTH_TOKEN=your_twilio_token (optional)
TWILIO_WHATSAPP_NUMBER=whatsapp:+1234567890 (optional)
ADMIN_WHATSAPP_NUMBER=whatsapp:+1234567890 (optional)
```

## Deployment Commands
- **Build Command**: `pip install -r requirements.txt`
- **Start Command**: `gunicorn server:app --host 0.0.0.0 --port $PORT`

## Your App Structure ✅
```
vet-clinic-ai-chatbot/
├── templates/          ✅ Flask templates
├── static/            ✅ CSS files  
├── server.py          ✅ Main Flask app
├── requirements.txt   ✅ Dependencies (with gunicorn)
├── render.yaml        ✅ Render config
└── database.db        ✅ SQLite database
```

## After Deployment
- Your app will be available at: `https://your-app-name.onrender.com`
- Render provides free SSL certificates
- Auto-deploys on every git push to main branch

## Troubleshooting
- Check Render logs if deployment fails
- Ensure all environment variables are set
- Database will be created automatically on first run
