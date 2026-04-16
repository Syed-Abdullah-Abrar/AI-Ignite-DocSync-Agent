"""
DocSync API - FastAPI Application

Main entry point for the DocSync backend service.
"""
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from concurrent.futures import ThreadPoolExecutor
import logging

from src.api.callbacks import router as uhi_router
from src.api.schemas import HealthCheckResponse
from src.graph.state import get_graph

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Thread pool for running sync graph in async context
_executor = ThreadPoolExecutor(max_workers=4)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan handler."""
    logger.info("DocSync API starting up...")
    yield
    logger.info("DocSync API shutting down...")
    _executor.shutdown(wait=True)


app = FastAPI(
    title="DocSync API",
    description="Healthcare Coordination Agent - ABDM UHI Integration",
    version="1.0.0",
    lifespan=lifespan
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production: specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(uhi_router)


@app.get("/health", response_model=HealthCheckResponse)
async def health_check():
    """Health check endpoint."""
    from datetime import datetime
    return HealthCheckResponse(
        status="healthy",
        timestamp=datetime.utcnow()
    )


@app.post("/whatsapp/webhook")
async def whatsapp_webhook(request: Request):
    """
    Receive WhatsApp messages via MCP webhook.
    
    This endpoint receives patient messages and orchestrates
    the LangGraph pipeline.
    """
    import asyncio
    
    body = await request.json()
    
    # Extract message data
    phone = body.get("from", "")
    message = body.get("text", "")
    session_id = body.get("session_id")
    
    # Initialize state
    from src.graph.state import PatientState
    state = PatientState(
        phone_number=phone,
        raw_message=message,
        session_id=session_id
    )
    
    # Run pipeline - use thread pool to avoid blocking
    graph = get_graph()
    
    # FIX: Run sync invoke in thread pool for async context
    loop = asyncio.get_event_loop()
    result = await loop.run_in_executor(
        _executor,
        lambda: graph.invoke(state)
    )
    
    return {"status": "processed", "session_id": session_id}


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "service": "DocSync",
        "version": "1.0.0",
        "status": "running"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
