"""Used in alembic migrations"""

import logging
import os
from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base


BASE_DIR = Path(__file__).resolve().parent

ENV = os.getenv("ENV", default=None)
DEBUG = ENV is None

if DEBUG:
    from utils.load_conf import LocalConfig

    LocalConfig.load(BASE_DIR=BASE_DIR)

    if not os.getenv("POSTGRES_PASSWORD"):
        raise Exception("Postgres password not present, cannot start debug server.")

DB_URL = f"postgresql://{os.getenv('POSTGRES_USER')}:{os.getenv('POSTGRES_PASSWORD')}@{os.getenv('POSTGRES_SERVER')}:{os.getenv('POSTGRES_PORT')}/{os.getenv('POSTGRES_DB')}"


Base = declarative_base()

try:
    engine = create_engine(DB_URL)
    engine.connect()
except Exception as e:
    logging.error(f"Is the database server up and running?")
    raise e
finally:
    engine.dispose()
