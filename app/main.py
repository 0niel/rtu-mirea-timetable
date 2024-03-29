import sentry_sdk
from fastapi import FastAPI
from fastapi_cache import FastAPICache
from fastapi_cache.backends.inmemory import InMemoryBackend
from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry.instrumentation.aiohttp_client import AioHttpClientInstrumentor
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.instrumentation.logging import LoggingInstrumentor
from opentelemetry.instrumentation.sqlalchemy import SQLAlchemyInstrumentor
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from sentry_sdk.integrations.asgi import SentryAsgiMiddleware
from starlette.middleware.cors import CORSMiddleware

from app.config import config
from app.database.connection import engine
from app.exceptions import add_exception_handlers, catch_unhandled_exceptions
from app.routers.campuses import router as campuses_router
from app.routers.degrees import router as degrees_router
from app.routers.disciplines import router as disciplines_router
from app.routers.groups import router as groups_router
from app.routers.institutes import router as institutes_router
from app.routers.lessons import router as lessons_router
from app.routers.lks import router as lks_router
from app.routers.periods import router as periods_router
from app.routers.rooms import router as rooms_router
from app.routers.teachers import router as teachers_router
from app.routers.utils import router as utils_router


def setup_profiler(app: FastAPI) -> None:
    resource = Resource.create(attributes={"service.name": config.PROFILER_SERVICE_NAME})

    tracer = TracerProvider(resource=resource)
    trace.set_tracer_provider(tracer)

    tracer.add_span_processor(
        BatchSpanProcessor(
            OTLPSpanExporter(
                endpoint=config.PROFILER_JAEGER_ENDPOINT,
                headers={"Authorization": f"Basic {config.PROFILER_AUTH_CREDENTIALS}"},
            )
        )
    )

    # Instrumentations
    FastAPIInstrumentor.instrument_app(app, tracer_provider=tracer)
    SQLAlchemyInstrumentor().instrument(engine=engine.sync_engine)
    LoggingInstrumentor().instrument(set_logging_format=True)
    AioHttpClientInstrumentor().instrument()


tags_metadata = [
    {"name": "campuses", "description": "Работа с кампусами"},
    {"name": "groups", "description": "Работа с группами"},
    {"name": "lessons", "description": "Работа с занятиями"},
    {"name": "teachers", "description": "Работа с преподавателями"},
    {"name": "rooms", "description": "Работа с аудиториями"},
    {"name": "institutes", "description": "Работа с институтами"},
    {"name": "disciplines", "description": "Работа с дисциплинами"},
    {"name": "periods", "description": "Работа с периодами"},
    {"name": "degrees", "description": "Работа со степенями"},
    {"name": "utils", "description": "Работа с утилитами"},
    {"name": "lks", "description": "Враппер для ЛКС РТУ МИРЭА"},
]

app = FastAPI(
    debug=config.DEBUG,
    openapi_tags=tags_metadata,
    openapi_url=f"{config.PREFIX}/openapi.json",
    title=config.TITLE,
    description=config.DESCRIPTION,
)

app.middleware("http")(catch_unhandled_exceptions)


@app.on_event("startup")
async def startup():
    FastAPICache.init(InMemoryBackend(), prefix="fastapi-cache")


if not config.SENTRY_DISABLE_LOGGING:
    sentry_sdk.init(dsn=config.SENTRY_DSN, attach_stacktrace=True)
app.add_middleware(SentryAsgiMiddleware)
add_exception_handlers(app)


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
app.include_router(teachers_router, tags=["teachers"])
app.include_router(rooms_router, tags=["rooms"])
app.include_router(institutes_router, tags=["institutes"])
app.include_router(disciplines_router, tags=["disciplines"])
app.include_router(periods_router, tags=["periods"])
app.include_router(degrees_router, tags=["degrees"])
app.include_router(utils_router, tags=["utils"])
app.include_router(lks_router, tags=["lks"])


if config.PROFILER_ENABLE:
    setup_profiler(app)
