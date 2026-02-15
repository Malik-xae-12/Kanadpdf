"""
FastAPI application entry-point.

Configures CORS, registers routers, and exposes a health-check endpoint.
"""

import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import get_settings
from app.routers import files

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s │ %(levelname)-8s │ %(name)s │ %(message)s",
)

# ---------------------------------------------------------------------------
# App factory
# ---------------------------------------------------------------------------
settings = get_settings()

app = FastAPI(
    title="Kanad PDF Viewer API",
    description=(
        "Serves PDF files stored in a Microsoft Fabric OneLake Lakehouse "
        "via Azure AD Service Principal authentication."
    ),
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# ---------------------------------------------------------------------------
# CORS
# ---------------------------------------------------------------------------
# ---------------------------------------------------------------------------
# CORS
# ---------------------------------------------------------------------------
origins = [
    "https://kanadpdf.vercel.app",
    "http://localhost:5173", 
    "*"                       
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------------------------------------------------------------------
# Routers
# ---------------------------------------------------------------------------
app.include_router(files.router, prefix="/api")


# ---------------------------------------------------------------------------
# Health check
# ---------------------------------------------------------------------------
@app.get("/health", tags=["system"])
async def health_check() -> dict:
    """Liveness probe – always returns 200."""
    return {"status": "healthy"}
