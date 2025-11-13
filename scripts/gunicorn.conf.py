# gunicorn.conf.py
import multiprocessing

bind = "0.0.0.0:8000"
workers = multiprocessing.cpu_count() * 2 + 1
worker_class = "uvicorn.workers.UvicornWorker"
worker_connections = 1000

# Logging
loglevel = "error"
errorlog = "-"
accesslog = "-"

# Timeouts
timeout = 60
keepalive = 10
graceful_timeout = 60

# Process naming
proc_name = "django_asgi"
worker_tmp_dir = "/dev/shm"