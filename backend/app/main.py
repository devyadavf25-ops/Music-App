import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .api.v1.router import api_router

app = FastAPI(
    title="Aura Music Platform API",
    description="Production-ready backend API supporting high-fidelity audio, controllable discovery, and hybrid personalization.",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
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
    return {
        "status": "healthy",
        "service": "Aura Music Platform Backend",
        "version": "1.0.0",
        "environment": os.getenv("ENVIRONMENT", "production" if os.getenv("RENDER") else "development"),
        "features": [
            "0-100% Recommendation Variance Slider",
            "4-Mode Shuffle System (Standard, True, Smart, Discovery)",
            "Hybrid Library Reconciliation",
            "Audiophile Honesty Stream Verification",
            "User-Centric Royalty Accounting"
        ]
    }

