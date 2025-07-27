# 🚀 Deploy Your Vet Clinic AI Chatbot to Render

## Quick Deployment Guide

### Step 1: Create Render Web Service
1. Go to [render.com](https://render.com) and sign up/login
2. Click "New +" → "Web Service"
3. Connect your GitHub repository: `vet-clinic-ai-chatbot`

### Step 2: Configure Service
- **Name**: `vet-clinic-ai-chatbot`
- **Environment**: `Python 3`
- **Build Command**: `pip install -r requirements.txt`
- **Start Command**: `python -m gunicorn server:app -c gunicorn.conf.py`

### Step 3: Set Environment Variables
In Render dashboard, add these environment variables:

**Required Variables:**
- `DATABASE_URL` - Your Supabase PostgreSQL URL
- `OPENAI_API_KEY` - Your OpenAI API key
- `SECRET_KEY` - Generate a new secure key
- `TWILIO_ACCOUNT_SID` - Your Twilio Account SID
- `TWILIO_AUTH_TOKEN` - Your Twilio Auth Token
- `TWILIO_WHATSAPP_NUMBER` - WhatsApp number (e.g., whatsapp:+14155238886)
- `ADMIN_WHATSAPP_NUMBER` - Admin WhatsApp number
- `SUPABASE_URL` - Your Supabase project URL
- `SUPABASE_ANON_KEY` - Your Supabase anon key
- `SUPABASE_SERVICE_ROLE_KEY` - Your Supabase service role key

### Step 4: Deploy
Click "Create Web Service" and wait for deployment to complete.

### Important Notes:
- Your Supabase database is already configured and ready
- Never commit your .env file to GitHub
- Use the environment variables tab in Render to set sensitive data
- Your app will be available at `https://your-app-name.onrender.com`

### Test After Deployment:
- Visit your app URL
- Test chatbot functionality
- Try booking an appointment
- Check admin panel access

🎉 Your veterinary clinic AI chatbot will be live!
