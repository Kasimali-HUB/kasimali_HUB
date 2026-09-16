from fastapi import APIRouter

router = APIRouter()


@router.get("/health", tags=["health"])
async def health_check() -> dict[str, str]:
    """Liveness check. Extend later with DB connectivity check if needed."""
    return {"status": "ok"}
