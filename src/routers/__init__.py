from fastapi import APIRouter

from .v1 import statistics, weather

api_v1_router = APIRouter()

api_v1_router.include_router(weather.router)
api_v1_router.include_router(statistics.router)
