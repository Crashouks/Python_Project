from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from tourist_routes.api import config

_is_sqlite = config.DATABASE_URL.startswith("sqlite")
if _is_sqlite and ":memory:" not in config.DATABASE_URL:
    db_path = config.DATABASE_URL.replace("sqlite:///", "", 1)
    from pathlib import Path

    Path(db_path).parent.mkdir(parents=True, exist_ok=True)

engine = create_engine(
    config.DATABASE_URL,
    connect_args={"check_same_thread": False} if _is_sqlite else {},
)
SessionLocal = sessionmaker(bind=engine, autoflush=False)


class Base(DeclarativeBase):
    pass


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
