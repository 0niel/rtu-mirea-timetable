from fastapi import APIRouter

from app.api.api_v1.endpoints import rooms, utils

api_router = APIRouter()
api_router.include_router(utils.router, prefix="/utils", tags=["utils"])
api_router.include_router(rooms.router, prefix="/rooms", tags=["rooms"])
