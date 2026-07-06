from fastapi import APIRouter
from backend.app.schemas import HealthResponse

router = APIRouter()

@router.get("/health", response_model=HealthResponse)
def get_health():
    return {
        "status": "ok",
        "live_llm_calls": False,
        "service": "leanbulk-coach-api",
        "version": "0.2.0"
    }
