"""
FastAPI Main Application
"""
import logging
import os
import sys
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

# Optional GZIP middleware
try:
    from fastapi.middleware.gzip import GZIPMiddleware
    HAS_GZIP = True
except ImportError:
    HAS_GZIP = False

# ------------------------------------------------------------------
# Path setup
# ------------------------------------------------------------------

# backend/app/main.py
# project_root/
# ├── LearnMate/
# │   └── backend/
# │       └── app/
# └── speech_module/

project_root = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(project_root))

# ------------------------------------------------------------------
# Logging setup
# ------------------------------------------------------------------

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("bhashasetu")

# ------------------------------------------------------------------
# Load environment variables
# ------------------------------------------------------------------

load_dotenv()

# ------------------------------------------------------------------
# Import API routers
# ------------------------------------------------------------------

from api.routes import router as api_router

# Try importing speech module (optional)
VOICE_MODULE_AVAILABLE = False
try:
    from speech_module.routes import router as voice_router
    VOICE_MODULE_AVAILABLE = True
    logger.info("Speech module loaded successfully")
except ImportError as e:
    logger.warning(f"Speech module not available: {e}")

# ------------------------------------------------------------------
# Create FastAPI app
# ------------------------------------------------------------------

app = FastAPI(
    title="BhashaSetu - Multilingual Smart Document Assistant",
    description="RAG-based document question answering system with multilingual support",
    version="1.0.0"
)

# ------------------------------------------------------------------
# Middleware
# ------------------------------------------------------------------

# ⚠️ CORS FIX:
# If allow_credentials=True, "*" is NOT allowed
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://localhost:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Optional compression
if HAS_GZIP:
    app.add_middleware(GZIPMiddleware, minimum_size=1000)

# ------------------------------------------------------------------
# Routers
# ------------------------------------------------------------------

app.include_router(api_router, prefix="/api", tags=["api"])

if VOICE_MODULE_AVAILABLE:
    app.include_router(voice_router, prefix="/api", tags=["voice"])

# ------------------------------------------------------------------
# Startup & Shutdown
# ------------------------------------------------------------------

@app.on_event("startup")
async def startup_event():
    """Verify configuration on startup"""
    deepseek_key = os.getenv("DEEPSEEK_API_KEY")

    if deepseek_key:
        logger.info("DeepSeek API key loaded")
    else:
        logger.warning("DeepSeek API key NOT found")

    if VOICE_MODULE_AVAILABLE:
        logger.info("Speech features enabled")
    else:
        logger.info(
            "Speech module disabled. Install dependencies with:\n"
            "pip install -r speech_module/requirements.txt"
        )


@app.on_event("shutdown")
async def shutdown_event():
    logger.info("Shutting down BhashaSetu application...")

# ------------------------------------------------------------------
# Health & Root
# ------------------------------------------------------------------

@app.get("/")
async def root():
    return {
        "message": "BhashaSetu - Multilingual Smart Document Assistant",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/api/health"
    }

# ------------------------------------------------------------------
# Local dev entrypoint
# ------------------------------------------------------------------

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
