"""
Database session and connection engine manager.
Supports PostgreSQL (Render / Supabase / Neon) and SQLite (local dev & testing).
"""

import os
import logging
from typing import Generator
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase

logger = logging.getLogger(__name__)

# Base class for declarative SQLAlchemy models
class Base(DeclarativeBase):
    pass


def get_database_url() -> str:
    raw_url = os.getenv("DATABASE_URL")
    if not raw_url or raw_url.strip() == "":
        # Zero-config local development database
        return "sqlite:///./aura_music.db"
    
    url = raw_url.strip()
    # Render and legacy providers use postgres://, but SQLAlchemy 2.x requires postgresql://
    if url.startswith("postgres://"):
        url = url.replace("postgres://", "postgresql://", 1)
    
    return url


DATABASE_URL = get_database_url()

# Configure engine arguments based on dialect
engine_kwargs = {}
if DATABASE_URL.startswith("sqlite"):
    engine_kwargs["connect_args"] = {"check_same_thread": False}
else:
    engine_kwargs["pool_pre_ping"] = True
    engine_kwargs["pool_size"] = 10
    engine_kwargs["max_overflow"] = 20

engine = create_engine(DATABASE_URL, **engine_kwargs)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db() -> Generator:
    """
    FastAPI dependency yielding an isolated database session per request.
    Automatically closes the session upon request completion.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
