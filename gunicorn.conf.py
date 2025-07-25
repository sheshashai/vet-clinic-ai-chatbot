import multiprocessing
import os

# Gunicorn configuration for Render deployment
bind = f"0.0.0.0:{os.getenv('PORT', 10000)}"
workers = 1  # Use single worker for free tier
worker_class = "sync"
worker_connections = 1000
timeout = 120
keepalive = 2
max_requests = 1000
max_requests_jitter = 100
preload_app = True

# Logging
accesslog = "-"
errorlog = "-"
loglevel = "info"

# Process naming
proc_name = "vet-clinic-chatbot"

# Worker restart
worker_tmp_dir = "/dev/shm"
