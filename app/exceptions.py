import traceback
from typing import Optional

import sentry_sdk
from fastapi import FastAPI, Request, status
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import HTTPException, RequestValidationError
from loguru import logger
from pydantic import UUID4, BaseModel
from starlette.responses import JSONResponse

from app.config import config


async def catch_unhandled_exceptions(request: Request, call_next) -> JSONResponse:
    try:
        return await call_next(request)
    except Exception as exc:
        if not config.SENTRY_DISABLE_LOGGING:
            sentry_sdk.set_tag("status_code", 500)
            sentry_sdk.capture_exception(exc)
        error = {
            "message": get_endpoint_message(request),
            "errors": [Message(message="Отказано в обработке из-за неизвестной ошибки на сервере")],
        }
        if not config.DEBUG:
            logger.info(traceback.format_exc())
            return JSONResponse(status_code=500, content=jsonable_encoder(error))
        else:
            raise


class Message(BaseModel):
    id: Optional[UUID4]
    message: str

    def __hash__(self):
        return hash((self.id, self.message))


endpoint_message = {
    ("GET", "/sbis/{id}/link"): "Ошибка получения ссылки на zip архив документа",
    ("GET", "/sbis/{id}/json"): "Ошибка получения json документа",
    ("GET", "/health/"): "Сервис недоступен",
    ("HEAD", "/health/"): "Сервис недоступен",
}


def get_endpoint_message(request: Request) -> Optional[str]:
    method, path = request.scope["method"], request.scope["path"]
    for path_parameter, value in request.scope["path_params"].items():
        path = path.replace(value, "{" + path_parameter + "}")
    return endpoint_message.get((method, path))


async def validation_handler(request: Request, exc) -> JSONResponse:
    errors = []
    for error in exc.errors():
        field = error["loc"][1]
        if type(field) == str:
            errors.append(Message(message=f'Поле {field} имеет некорректное значение ({error["type"]})'))
        else:
            errors.append(Message(message=f'Тело запроса содержит некорректные значения ({error["type"]})'))

    error = {"message": get_endpoint_message(request), "errors": list(set(errors))}

    if not config.SENTRY_DISABLE_LOGGING:
        try:
            raise HTTPException(400, error)
        except HTTPException as e:
            sentry_sdk.set_tag("status_code", 400)
            sentry_sdk.capture_exception(e)

    return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content=jsonable_encoder(error))


async def logging_handler(request: Request, exc: HTTPException) -> JSONResponse:
    sentry_sdk.set_tag("status_code", exc.status_code)
    sentry_sdk.capture_exception(exc)
    error = {"message": get_endpoint_message(request), "errors": exc.detail}
    return JSONResponse(status_code=exc.status_code, content=jsonable_encoder(error))


def add_exception_handlers(app: FastAPI) -> None:
    # важен порядок хэндлеров
    app.add_exception_handler(RequestValidationError, validation_handler)
    app.add_exception_handler(HTTPException, logging_handler)
