from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import func, select

from app.api.v1.router import api_router
from app.core.config import get_settings
from app.db.base import Base
from app.db.models import Client
from app.db.seed import seed_demo_data
from app.db.session import async_session_factory, engine

settings = get_settings()

app = FastAPI(title=settings.app_name)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix=settings.api_v1_prefix)


@app.on_event("startup")
async def create_tables_and_seed_in_dev() -> None:
    """
    Dev-only convenience so `uvicorn app.main:app` works with nothing else
    running - no Docker, no separate Postgres install. Production deploys
    should use real migrations (Alembic) instead of create_all, and should
    never auto-seed demo data.
    """
    if settings.environment != "development":
        return

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with async_session_factory() as session:
        existing = (await session.execute(select(func.count()).select_from(Client))).scalar_one()
        if existing == 0:
            await seed_demo_data(session)


@app.get("/", tags=["root"])
async def root() -> dict[str, str]:
    return {"app": settings.app_name, "environment": settings.environment}
