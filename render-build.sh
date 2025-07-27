#!/bin/bash
# Render.com Deployment Script
# This script runs during build phase

echo "🚀 Starting Render.com deployment..."

# Upgrade pip and install requirements
echo "📦 Installing Python dependencies..."
python3.11 -m pip install --upgrade pip setuptools wheel
pip install -r requirements.txt

echo "✅ Dependencies installed successfully"

# Test database connection (optional)
echo "🔍 Testing environment variables..."
if [ -z "$DATABASE_URL" ]; then
    echo "⚠️  WARNING: DATABASE_URL not set"
else
    echo "✅ DATABASE_URL configured"
fi

if [ -z "$OPENAI_API_KEY" ]; then
    echo "⚠️  WARNING: OPENAI_API_KEY not set"
else
    echo "✅ OPENAI_API_KEY configured"
fi

echo "🎉 Build completed successfully!"
