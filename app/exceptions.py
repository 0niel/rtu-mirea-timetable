import traceback
from typing import List, Optional

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
    ("GET", "/"): "Ошибка получения клиентской страницы групп",
    ("GET", "/group/{name}"): "Ошибка клиентской страницы указанной группы",
    ("GET", "/api/campus"): "Ошибка получения списка кампусов",
    ("GET", "/api/campus/{id}"): "Ошибка получения кампуса по идентификатору",
    ("GET", "/api/campus/{id}/rooms"): "Ошибка получения аудиторий кампуса",
    ("GET", "/api/group"): "Ошибка получения списка групп",
    ("GET", "/api/group/{id}"): "Ошибка получения группы по идентификатору",
    ("GET", "/api/group/name/{name}"): "Ошибка получения группы по имени",
    ("GET", "/api/schedule"): "Ошибка получения списка занятий",
    ("GET", "/api/schedule/id/{id}"): "Ошибка получения занятия по идентификатору",
    ("GET", "/api/schedule/room/{id}"): "Ошибка получения расписания аудитории",
    ("GET", "/api/schedule/call"): "Ошибка получения списка звонков",
    ("GET", "/api/schedule/call/{id}"): "Ошибка получения звонка по идентификатору",
    ("GET", "/api/schedule/type"): "Ошибка получения списка типов занятий",
    ("GET", "/api/schedule/type/{id}"): "Ошибка получения типа занятия по идентификатору",
    ("GET", "/api/teacher"): "Ошибка получения списка преподавателей",
    ("GET", "/api/teacher/{id}"): "Ошибка получения преподавателя по идентификатору",
    ("GET", "/api/teacher/search/{name}"): "Ошибка поиска преподавателей",
    ("GET", "/api/room"): "Ошибка получения списка аудиторий",
    ("GET", "/api/room/{id}"): "Ошибка получения аудитории по идентификатору",
    ("GET", "/api/room/search/{name}"): "Ошибка поиска аудитории",
    ("GET", "/api/institute"): "Ошибка получения списка институтоы",
    ("GET", "/api/institute/{id}"): "Ошибка получения института по идентификатору",
    ("GET", "/api/discipline"): "Ошибка получения списка дисциплин",
    ("GET", "/api/discipline/{id}"): "Ошибка получения дисциплины по идентификатору",
    ("GET", "/api/discipline/name/{name}"): "Ошибка получения дисциплины по имени",
    ("GET", "/api/period"): "Ошибка получения списка периодов",
    ("GET", "/api/period/{id}"): "Ошибка получения периода по идентификатору",
    ("GET", "/api/degree"): "Ошибка получения списка степеней",
    ("GET", "/api/degree/{id}"): "Ошибка получения степени по идентификатору",
    ("POST", "/api/parse-schedule"): "Ошибка запуска задачи парсинга расписания",
    ("GET", "/api/lks/{group_name}"): "Ошибка получения расписания группы в формате ЛКС",
}


def get_endpoint_message(request: Request) -> Optional[str]:
    method, path = request.scope["method"], request.scope["path"]
    for path_parameter, value in request.scope["path_params"].items():
        path = path.replace(value, "{" + path_parameter + "}")
    return endpoint_message.get((method, path))


class ValidationUtils:
    @staticmethod
    def validate_type_error(error):
        field = error["loc"][-1]
        type_ = error["type"].split(".")[-1]
        return f'Поле "{field}" Имеет неверный тип данных. Укажите "{type_}"'

    @staticmethod
    def validate_const(error):
        field = error["loc"][-1]
        value = error["ctx"]["given"]
        allowed_values = error["ctx"]["permitted"]
        return (
            f'Поле "{field}" имеет некорректное значение, Вы указали  "{value}". Возможные значения: {allowed_values}'
        )

    @staticmethod
    def validate_invalid_discriminator(error):
        allowed_values = error["ctx"]["allowed_values"]
        discriminator_value = error["ctx"]["discriminator_key"]
        user_value = error["ctx"]["discriminator_value"]

        return (
            f'Поле "{discriminator_value}" является обязательным. Вы указали "{user_value}".'
            f"Возможные значения: {allowed_values}"
        )

    @staticmethod
    def validate_missing(error):
        field = error["loc"][-1]
        return f'Поле "{field}" является обязательным'


templates_function = {
    "missing": ValidationUtils.validate_missing,
    "const": ValidationUtils.validate_const,
    "": ValidationUtils.validate_type_error,
    "invalid_discriminator": ValidationUtils.validate_invalid_discriminator,
}


class ValidationHandler:
    @classmethod
    async def _send_to_sentry(cls, request: Request, error):
        if not config.SENTRY_DISABLE_LOGGING:
            try:
                raise HTTPException(400, error)
            except HTTPException as e:
                sentry_sdk.set_tag("status_code", 400)
                sentry_sdk.capture_exception(e)

    @classmethod
    async def _build_final_error(cls, request: Request, errors: List[Message]):
        return {"message": get_endpoint_message(request), "errors": list(set(errors))}

    @classmethod
    async def _build_message(cls, type_: str, error: dict):
        try:
            if type_ in templates_function.keys():
                return templates_function[type_](error)
            else:
                return templates_function[""](error)
        except KeyError:
            return error["msg"]

    @classmethod
    async def validation_handler(cls, request: Request, exc):
        errors = []
        for error in exc.errors():
            type_ = error["type"].split(".")[-1]
            message = await cls._build_message(type_, error)
            errors.append(Message(message=message))

        error = await cls._build_final_error(request, errors)
        await cls._send_to_sentry(request, error)

        return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content=jsonable_encoder(error))


async def logging_handler(request: Request, exc: HTTPException):
    sentry_sdk.set_tag("status_code", exc.status_code)
    sentry_sdk.capture_exception(exc)
    error = {"message": get_endpoint_message(request), "errors": exc.detail}
    return JSONResponse(status_code=exc.status_code, content=jsonable_encoder(error))


def add_exception_handlers(app: FastAPI):
    app.add_exception_handler(RequestValidationError, ValidationHandler.validation_handler)
    app.add_exception_handler(HTTPException, logging_handler)
