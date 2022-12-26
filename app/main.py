from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware

from app.config import config
from app.routers.campuses import router as campuses_router
from app.routers.groups import router as groups_router
from app.routers.lessons import router as lessons_router
from app.routers.lks import router as lks_router
from app.routers.rooms import router as rooms_router
from app.routers.utils import router as utils_router

tags_metadata = [
    {"name": "campuses", "description": "Работа с кампусами"},
    {"name": "groups", "description": "Работа с группами"},
    {"name": "lessons", "description": "Работа с занятиями"},
    {"name": "rooms", "description": "Работа с аудиториями"},
    {"name": "utils", "description": "Работа с утилитами"},
    {"name": "lks", "description": "Враппер для ЛКС РТУ МИРЭА"},
]

app = FastAPI(
    debug=config.DEBUG,
    openapi_tags=tags_metadata,
    openapi_url=f"{config.BACKEND_PREFIX}/openapi.json",
    title=config.BACKEND_TTILE,
    description=config.BACKEND_DESCRIPTION,
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(campuses_router, tags=["campuses"])
app.include_router(groups_router, tags=["groups"])
app.include_router(lessons_router, tags=["lessons"])
app.include_router(rooms_router, tags=["rooms"])
app.include_router(utils_router, tags=["utils"])
app.include_router(lks_router, tags=["lks"])
