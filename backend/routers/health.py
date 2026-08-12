from fastapi import APIRouter
from models import HealthResponse, WolframHealthResponse
from services.wolfram_client import check_wolfram_health

router = APIRouter()


@router.get("/health", response_model=HealthResponse)
async def health():
    return {"status": "ok"}


@router.get("/health/wolfram", response_model=WolframHealthResponse)
async def health_wolfram():
    available, mode = check_wolfram_health()
    response = {"wolfram_available": available, "mode": mode}
    if not available:
        response["note"] = "Using local LP fallback solver — Wolfram unavailable"
    return response
