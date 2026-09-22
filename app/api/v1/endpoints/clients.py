from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import Client
from app.db.session import get_db
from app.schemas.dashboard import ClientOut

router = APIRouter()


@router.get("/clients", response_model=list[ClientOut], tags=["clients"])
async def list_clients(db: AsyncSession = Depends(get_db)) -> list[Client]:
    result = await db.execute(select(Client).order_by(Client.name))
    return list(result.scalars().all())
