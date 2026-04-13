from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import logging
import requests
import chromadb
import json

# Configure structured logging
class StructuredLogger:
    def __init__(self, name):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.INFO)

    def info(self, message, **kwargs):
        if kwargs:
            self.logger.info(f"{message} | Context: {json.dumps(kwargs)}")
        else:
            self.logger.info(message)

    def warning(self, message, **kwargs):
        if kwargs:
            self.logger.warning(f"{message} | Context: {json.dumps(kwargs)}")
        else:
            self.logger.warning(message)

    def error(self, message, **kwargs):
        if kwargs:
            self.logger.error(f"{message} | Context: {json.dumps(kwargs)}")
        else:
            self.logger.error(message)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)
logger = StructuredLogger(__name__)

# Initialize the FastAPI app
app = FastAPI(
    title="MindBridge API",
    description="API for MindBridge - ML Bootcamp Project",
    version="1.0.0"
)

# CORS middleware - restrict in production
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For local development only
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Import routers
from backend.app.routes import upload, chat

# Register routers
app.include_router(upload.router, prefix="/upload", tags=["upload"])
app.include_router(chat.router, prefix="/chat", tags=["chat"])

@app.on_event("startup")
async def startup_event():
    """Initialize services on startup"""
    logger.info("Starting up MindBridge API")

    # Validate configuration
    try:
        from app.core.config import Config
        if not Config.validate_config():
            logger.error("Configuration validation failed. Please check your .env file.")
            # Note: We don't exit here to allow the API to start for debugging purposes
        else:
            logger.info("Configuration validation passed")
    except Exception as e:
        logger.error(f"Error during configuration validation: {str(e)}")

    # Core services initialization can be done here if needed

@app.on_event("shutdown")
async def shutdown_event():
    """Clean up on shutdown"""
    logger.info("Shutting down MindBridge API")

@app.get("/")
async def root():
    """Root endpoint"""
    return {"message": "Welcome to MindBridge API"}

@app.get("/health")
async def health_check():
    """Basic health check endpoint"""
    return {"status": "healthy", "service": "MindBridge API"}

@app.get("/health/detailed")
async def detailed_health_check():
    """Detailed health check endpoint"""
    health_status = {
        "status": "healthy",
        "services": {}
    }

    # Check Ollama service
    try:
        from app.core.config import Config
        ollama_url = f"{Config.OLLAMA_HOST}/api/tags"
        response = requests.get(ollama_url, timeout=5)
        health_status["services"]["ollama"] = "healthy" if response.status_code == 200 else "unhealthy"
    except Exception as e:
        logger.warning(f"Ollama health check failed: {str(e)}")
        health_status["services"]["ollama"] = f"unhealthy: {str(e)}"

    # Check ChromaDB
    try:
        from app.core.config import Config
        client = chromadb.PersistentClient(
            path=Config.CHROMA_PERSIST_DIRECTORY
        )
        # Simple check to see if we can access the client
        client.list_collections()
        health_status["services"]["chromadb"] = "healthy"
    except Exception as e:
        logger.warning(f"ChromaDB health check failed: {str(e)}")
        health_status["services"]["chromadb"] = f"unhealthy: {str(e)}"

    # Overall status
    if any("unhealthy" in status for status in health_status["services"].values()):
        health_status["status"] = "degraded"

    return health_status

if __name__ == "__main__":
    import uvicorn
    from app.core.config import Config

    uvicorn.run(
        "app.main:app",
        host=Config.API_HOST,
        port=Config.API_PORT,
        reload=True
    )