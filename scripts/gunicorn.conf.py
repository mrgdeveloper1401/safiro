# gunicorn.conf.py version 25
import multiprocessing

bind = "0.0.0.0:8000"
workers = multiprocessing.cpu_count() * 2
worker_class = "asgi"
worker_connections = 1000 # max connection management per worker
max_requests = 10000 # restart worker when process 10000 requests
keepalive = 5 # max time open connection between backend and nginx
timeout = 120 # Maximum processing time for a request
graceful_timeout = 30 # max timeworker shutdown

# performance tuning
asgi_loop = 'auto'
asgi_lifespan = "auto"

# Logging
loglevel = "error"
errorlog = "-"
# accesslog = "-"

