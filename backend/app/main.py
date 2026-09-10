import os
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text

from .api.v1.router import api_router
from .db.init_db import init_db
from .db.session import DATABASE_URL, SessionLocal

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Ensure database schema exists and seed initial data
    try:
        init_db()
        logger.info("Database schema initialized and verified.")
    except Exception as e:
        logger.error(f"Error during database initialization: {e}", exc_info=True)
    yield


app = FastAPI(
    title="Aura Music Platform API",
    description="Production-ready backend API supporting high-fidelity audio, controllable discovery, hybrid personalization, and persistent relational storage.",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# Environment-aware CORS configuration
cors_env = os.getenv("CORS_ORIGINS", "*")
if cors_env == "*":
    allowed_origins = ["*"]
else:
    allowed_origins = [origin.strip() for origin in cors_env.split(",") if origin.strip()]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_origin_regex=r"https://.*\.onrender\.com|http://localhost:\d+|http://127\.0\.0\.1:\d+",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix="/api")


@app.get("/")
def health_check():
    db_status = "connected"
    try:
        with SessionLocal() as db:
            db.execute(text("SELECT 1"))
    except Exception as e:
        db_status = f"unreachable: {str(e)}"

    return {
        "status": "healthy",
        "service": "Aura Music Platform Backend",
        "version": "1.0.0",
        "database": db_status,
        "database_type": "postgresql" if "postgresql" in DATABASE_URL else "sqlite",
        "environment": os.getenv("ENVIRONMENT", "production" if os.getenv("RENDER") else "development"),
        "features": [
            "0-100% Recommendation Variance Slider",
            "4-Mode Shuffle System (Standard, True, Smart, Discovery)",
            "Hybrid Library Reconciliation",
            "Audiophile Honesty Stream Verification",
            "User-Centric Royalty Accounting",
            "Persistent Relational Database (PostgreSQL / SQLite)"
        ]
    }
