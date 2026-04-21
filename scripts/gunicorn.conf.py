# gunicorn.conf.py
import multiprocessing

bind = "0.0.0.0:8000"
workers = multiprocessing.cpu_count() * 2
worker_class = "uvicorn.workers.UvicornWorker"
worker_connections = 1000

# Logging
loglevel = "error"
errorlog = "-"
# accesslog = "-"

# Timeouts
# timeout = 60
# keepalive = 1
# graceful_timeout = 60
