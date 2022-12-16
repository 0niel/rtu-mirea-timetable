import traceback
from typing import List, Optional

from fastapi import FastAPI, Request, status
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import HTTPException, RequestValidationError
from loguru import logger
from pydantic import UUID4, BaseModel
from starlette.responses import JSONResponse

from app.config import config


async def catch_unhandled_exceptions(request: Request, call_next):
    try:
        return await call_next(request)
    except Exception:
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
    ("POST", "/api/signin"): "Ошибка входа в систему",
    ("POST", "/api/signup"): "Ошибка регистрации в системе",
    ("GET", "/api/user/me"): "Ошибка получения пользователя",
    ("POST", "/api/user"): "Ошибка создания пользователя",
    ("GET", "/api/user"): "Ошибка получения всех пользователей",
    ("GET", "/api/user/{id}"): "Ошибка получения пользователя по id",
    ("GET", "/api/user/email/{email}"): "Ошибка получения пользователя по email",
    ("PUT", "/api/user/{id}"): "Ошибка изменения пользователя по id",
    ("PATCH", "/api/user/{id}"): "Ошибка частичного изменения пользователя по id",
    ("DELETE", "/api/user/{id}"): "Ошибка удаления пользователя по id",
    ("POST", "/api/category"): "Ошибка создания категории",
    ("GET", "/api/category"): "Ошибка получения всех категорий",
    ("GET", "/api/category/{id}"): "Ошибка получения категорий по id",
    ("PUT", "/api/category/{id}"): "Ошибка изменения категорий по id",
    ("PATCH", "/api/category/{id}"): "Ошибка частичного изменения категорий по id",
    ("DELETE", "/api/category/{id}"): "Ошибка удаления категорий по id",
    ("POST", "/api/comment"): "Ошибка создания комментария",
    ("GET", "/api/comment"): "Ошибка получения всех комментариев",
    ("GET", "/api/comment/{id}"): "Ошибка получения комментария по id",
    ("PUT", "/api/comment/{id}"): "Ошибка изменения комментария по id",
    ("PATCH", "/api/comment/{id}"): "Ошибка частичного изменения комментария по id",
    ("DELETE", "/api/comment/{id}"): "Ошибка удаления комментария по id",
    ("POST", "/api/media"): "Ошибка создания медиа-файла",
    ("GET", "/api/media"): "Ошибка получения всех медиа-файлов",
    ("GET", "/api/media/{id}"): "Ошибка получения медиа-файла по id",
    ("PUT", "/api/media/{id}"): "Ошибка изменения медиа-файла по id",
    ("PATCH", "/api/media/{id}"): "Ошибка частичного изменения медиа-файла по id",
    ("DELETE", "/api/media/{id}"): "Ошибка удаления медиа-файла по id",
    ("POST", "/api/news"): "Ошибка создания новости",
    ("GET", "/api/news"): "Ошибка получения всех новостей",
    ("GET", "/api/news/{id}"): "Ошибка получения новости по id",
    ("PUT", "/api/news/{id}"): "Ошибка изменения новости по id",
    ("PATCH", "/api/news/{id}"): "Ошибка частичного изменения новости по id",
    ("DELETE", "/api/news/{id}"): "Ошибка удаления новости по id",
    ("POST", "/api/news/like/{id}"): "Ошибка лайка новости по id",
    ("POST", "/api/news/dislike/{id}"): "Ошибка дизлайка новости по id",
}


def get_endpoint_message(request: Request):
    method, path = request.scope["method"], request.scope["path"]
    for path_parameter, value in request.scope["path_params"].items():
        path = path.replace(value, "{" + path_parameter + "}")
    return endpoint_message.get((method, path))


class ValidationUtils:
    @staticmethod
    def validate_type_error(error):
        field = error["loc"][-1]
        type_ = error["type"].split(".")[-1]
        msg = error["msg"]
        return f'Поле "{field}" Имеет неверный тип данных. Укажите "{type_}" ({msg})'

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
            f"Возможные значения {allowed_values}"
        )

    @staticmethod
    def validate_missing_discriminator(error):
        discriminator_value = error["ctx"]["discriminator_key"]

        return f'Поле "{discriminator_value}" является обязательным.'

    @staticmethod
    def validate_missing(error):
        field = error["loc"][-1]
        return f"Поле {field} является обязательным"


templates_function = {
    "missing": ValidationUtils.validate_missing,
    "const": ValidationUtils.validate_const,
    "": ValidationUtils.validate_type_error,
    "invalid_discriminator": ValidationUtils.validate_invalid_discriminator,
    "missing_discriminator": ValidationUtils.validate_missing_discriminator,
}


class ValidationHandler:
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

        return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content=jsonable_encoder(error))


async def logging_handler(request: Request, exc: HTTPException):
    error = {"message": get_endpoint_message(request), "errors": exc.detail}
    return JSONResponse(status_code=exc.status_code, content=jsonable_encoder(error))


def add_exception_handlers(app: FastAPI):
    app.add_exception_handler(RequestValidationError, ValidationHandler.validation_handler)
    app.add_exception_handler(HTTPException, logging_handler)
