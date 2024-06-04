"""Dynamically create a configuration for gunicorn workers"""

import multiprocessing
import os


host = os.getenv("HOST", "0.0.0.0")
port = os.getenv("PORT", "5000")
use_loglevel = os.getenv("LOG_LEVEL", "info")

use_bind = f"{host}:{port}"

workers_per_core = os.getenv("WORKERS_PER_CORE", "1")
web_concurrency_str = os.getenv("WEB_CONCURRENCY", None)

cores = multiprocessing.cpu_count()

default_web_concurrency = workers_per_core * float(workers_per_core)

web_concurrency = max(int(default_web_concurrency), 2)

loglevel = use_loglevel
workers = web_concurrency
bind = use_bind
keepalive = 120
