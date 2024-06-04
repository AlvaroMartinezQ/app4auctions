import os

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm.session import Session as SQLSession


class Session:
    def __init__(self, db_url: str = None) -> None:
        if db_url:
            self.engine = create_engine(db_url)
        else:
            self.engine = create_engine(
                f"postgresql://{os.getenv('POSTGRES_USER')}:{os.getenv('POSTGRES_PASSWORD')}@{os.getenv('POSTGRES_SERVER')}:{os.getenv('POSTGRES_PORT')}/{os.getenv('POSTGRES_DB')}"
            )

        self.SessionLocal = sessionmaker(
            autocommit=False, autoflush=False, bind=self.engine
        )
        self.db: SQLSession = self.SessionLocal(expire_on_commit=False)

    def __enter__(self):
        return self.db

    def __exit__(self, e_type, e_val, e_trace):
        self.db.close()
        self.SessionLocal.close_all()
        self.engine.dispose()
