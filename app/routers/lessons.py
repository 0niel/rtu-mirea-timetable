from app.config import config
from fastapi import APIRouter

router = APIRouter(prefix=config.BACKEND_PREFIX)
