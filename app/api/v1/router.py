from fastapi import APIRouter

from app.api.v1.endpoints import health

api_router = APIRouter()
api_router.include_router(health.router)

# Future routers plug in here, e.g.:
# from app.api.v1.endpoints import clients, payroll_runs, exceptions
# api_router.include_router(clients.router, prefix="/clients", tags=["clients"])
