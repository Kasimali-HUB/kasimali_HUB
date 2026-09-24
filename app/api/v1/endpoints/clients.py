from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import Client
from app.db.session import get_db
from app.schemas.dashboard import ClientCreate, ClientOut

router = APIRouter()


@router.get("/clients", response_model=list[ClientOut], tags=["clients"])
async def list_clients(db: AsyncSession = Depends(get_db)) -> list[Client]:
    result = await db.execute(select(Client).order_by(Client.name))
    return list(result.scalars().all())


@router.post("/clients", response_model=ClientOut, status_code=201, tags=["clients"])
async def create_client(payload: ClientCreate, db: AsyncSession = Depends(get_db)) -> Client:
    name = payload.name.strip()
    if not name:
        raise HTTPException(status_code=422, detail="Client name cannot be empty.")

    existing = await db.execute(select(Client).where(Client.name == name))
    if existing.scalar_one_or_none() is not None:
        raise HTTPException(status_code=409, detail=f'A client named "{name}" already exists.')

    client = Client(name=name, country_code=payload.country_code)
    db.add(client)
    await db.commit()
    await db.refresh(client)
    return client
