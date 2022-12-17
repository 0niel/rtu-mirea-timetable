from fastapi import APIRouter

from app.config import config

router = APIRouter(prefix=config.BACKEND_PREFIX)
