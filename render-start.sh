#!/bin/bash
# Render.com Start Script
# This script runs when the service starts

echo "🌟 Starting Vet Clinic AI Chatbot..."

# Set production environment
export FLASK_ENV=production

# Start the application with Gunicorn
echo "🚀 Starting Gunicorn server..."
exec python -m gunicorn server:app -c gunicorn.conf.py
