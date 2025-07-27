import multiprocessing
import os

# Gunicorn configuration for Render deployment with PostgreSQL
bind = f"0.0.0.0:{os.getenv('PORT', 10000)}"
workers = 1  # Use single worker for free tier
worker_class = "sync"
worker_connections = 1000
timeout = 120  # Increased for LLM requests
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

# PostgreSQL connection pool settings
def when_ready(server):
    """Called when the server is ready."""
    server.log.info("Server is ready. PostgreSQL connections will be pooled.")

def worker_int(worker):
    """Called when a worker receives the INT or QUIT signal."""
    worker.log.info("Worker received INT or QUIT signal")

def pre_fork(server, worker):
    """Called before a worker is forked."""
    server.log.info("Worker spawned (pid: %s)", worker.pid)
