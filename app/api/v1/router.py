from fastapi import APIRouter

from app.api.v1.endpoints import clients, dashboard, exceptions, health, legislation, payroll_runs

api_router = APIRouter()
api_router.include_router(health.router)
api_router.include_router(legislation.router)
api_router.include_router(clients.router)
api_router.include_router(dashboard.router)
api_router.include_router(payroll_runs.router)
api_router.include_router(exceptions.router)
