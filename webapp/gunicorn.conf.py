"""
Production Gunicorn Configuration for India's Journey on Azure.
Optimized for resource-constrained environments (Azure App Service B1 Linux / Container Apps).
Keeps total memory footprint well under 250 MB while supporting concurrent throughput via gthread.
"""
import os

# Server socket
port = os.environ.get('PORT', '8000')
bind = f"0.0.0.0:{port}"

# Worker processes: 2 workers x 2 threads = 4 concurrent requests
workers = int(os.environ.get('WEB_CONCURRENCY', '2'))
threads = int(os.environ.get('GUNICORN_THREADS', '2'))
worker_class = os.environ.get('GUNICORN_WORKER_CLASS', 'gthread')

# Worker lifecycle & memory recycling
timeout = int(os.environ.get('GUNICORN_TIMEOUT', '60'))
graceful_timeout = int(os.environ.get('GUNICORN_GRACEFUL_TIMEOUT', '30'))
keepalive = int(os.environ.get('GUNICORN_KEEPALIVE', '5'))

# Periodically restart workers to prevent slow memory leaks in low-resource environments
max_requests = int(os.environ.get('GUNICORN_MAX_REQUESTS', '1000'))
max_requests_jitter = int(os.environ.get('GUNICORN_MAX_REQUESTS_JITTER', '100'))

# Logging to stdout/stderr for Azure App Service & Container Insights
accesslog = '-'
errorlog = '-'
loglevel = os.environ.get('DJANGO_LOG_LEVEL', 'info').lower()
capture_output = True
