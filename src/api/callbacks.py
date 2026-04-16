"""
UHI Callbacks - Webhook Handlers

FastAPI endpoints for ABDM UHI callback processing.
"""
from fastapi import APIRouter, Request, HTTPException
from pydantic import BaseModel
from typing import Optional
from src.api.uhi_client import UHIClient


router = APIRouter(prefix="/uhi", tags=["uhi"])


class SearchCallbackRequest(BaseModel):
    """Request model for /on_search callback."""
    requestId: str
    transactionId: str
    results: list[dict]


class ConfirmCallbackRequest(BaseModel):
    """Request model for /on_confirm callback."""
    requestId: str
    appointmentId: str
    status: str
    details: Optional[dict] = None


@router.post("/on_search")
async def on_search(request: SearchCallbackRequest):
    """
    Handle /on_search callback from UHI Gateway.
    
    Receives doctor search results and processes them for patient presentation.
    """
    client = UHIClient()
    
    try:
        result = await client.on_search_callback(request.dict())
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/on_confirm")
async def on_confirm(request: ConfirmCallbackRequest):
    """
    Handle /on_confirm callback from UHI Gateway.
    
    Receives appointment confirmation and sends notification to patient.
    """
    client = UHIClient()
    
    try:
        result = await client.on_confirm_callback(request.dict())
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
