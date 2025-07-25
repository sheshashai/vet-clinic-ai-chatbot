#!/bin/bash
# Render startup script

echo "Starting Vet Clinic AI Chatbot..."
echo "Python version: $(python --version)"
echo "Pip version: $(pip --version)"

# Initialize database
echo "Initializing database..."
python -c "from server import init_db; init_db()"

# Start the application
echo "Starting gunicorn server..."
exec python -m gunicorn server:app -c gunicorn.conf.py
