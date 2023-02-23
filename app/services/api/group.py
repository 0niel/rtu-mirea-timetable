from typing import List, Optional

from fastapi import HTTPException
from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession

from app import models
from app.database import tables
from app.services.db import GroupDBService


class GroupService:
    """Сервис для работы с группами."""

    @classmethod
    async def get_groups(cls, db: AsyncSession, groups_ids: Optional[int], limit: int, offset: int) -> models.Groups:
        """Получение списка всех групп"""

        logger.debug("Запрос на получение списка групп")

        groups = await cls._get_multiple(db=db, groups_ids=groups_ids, limit=limit, offset=offset)
        logger.debug(f"Группы получены: {groups}")

        return cls._translate_groups_to_response_model(groups)

    @classmethod
    async def get_group(cls, db: AsyncSession, id_: int) -> models.Group:
        """Получение группы по идентификатору"""

        logger.debug(f"Запрос на получение группы с {id_ = }")

        group = await cls._get_one(db=db, id_=id_)
        logger.debug(f"Группа получена: {group}")

        return models.Group.from_orm(group)

    @classmethod
    async def get_group_by_name(cls, db: AsyncSession, name: str, period_id: Optional[int] = None) -> models.Group:
        """Получение группы по имени"""

        logger.debug(f"Запрос на получение группы с {name = }")

        group = await cls._get_one_by_name(db=db, name=name, period_id=period_id)
        logger.debug(f"Группа получена: {group}")

        return models.Group.from_orm(group)

    @classmethod
    async def create_group(cls, db: AsyncSession, group: models.GroupCreate) -> models.Group:
        """Создание группы"""

        logger.debug(f"Запрос на создание группы: {group =}")

        await cls._check_group_existence_with_name(db=db, name=group.name)
        # await cls._check_group_existence_with_period_id(db=db, name=group.period_id)
        # await cls._check_group_existence_with_degree_id(db=db, name=group.degree_id)
        # await cls._check_group_existence_with_institute_id(db=db, name=group.institute_id)

        db_group = await GroupDBService.create(db=db, group=group)
        await db.commit()
        await db.refresh(db_group)

        logger.info(f"Создана новая группа: {group = }")

        return models.Group.from_orm(db_group)

    @classmethod
    async def _get_one(cls, db: AsyncSession, id_: int) -> tables.Group:
        """Получение группы по идентификатору и проверка на существование"""

        group = await GroupDBService.get_group(db=db, id_=id_)
        if not group:
            logger.warning(f"Группа с {id_ = } не найдена")
            raise HTTPException(status_code=404, detail=f"Группа {id_} не найдена")
        return group

    @classmethod
    async def _get_one_by_name(cls, db: AsyncSession, name: str, period_id: Optional[int] = None) -> tables.Group:
        """Получение группы по имени и проверка на существование"""

        group = await GroupDBService.get_group_by_name(db=db, name=name, period_id=period_id)
        if not group:
            logger.warning(f"Группа с {name = } не найдена")
            raise HTTPException(status_code=404, detail=f"Группа {name} не найдена")
        return group

    @classmethod
    async def _get_multiple(
        cls, db: AsyncSession, groups_ids: Optional[int], limit: int, offset: int
    ) -> List[tables.Group]:
        """Получение группы по имени и проверка на существование"""

        groups = await GroupDBService.get_groups(db=db, groups_ids=groups_ids, limit=limit, offset=offset)
        if not groups:
            logger.warning("Группы не найдены")
            raise HTTPException(status_code=404, detail="Группы не найдены")
        return groups

    @classmethod
    async def _check_group_existence_with_name(cls, db: AsyncSession, name: str) -> None:
        """Проверка существования группы с name"""

        logger.debug(f"Проверяем существование группы с {name = }")

        if await GroupDBService.get_group_by_name(db=db, name=name):
            logger.warning(f"Попытка создать группу с уже существующим name: {name}")
            raise HTTPException(status_code=409, detail="Группа с таким названием уже существует")

        logger.debug(f"Группы с {name = } ещё нет")

    @classmethod
    def _translate_groups_to_response_model(cls, groups: List[tables.Group]) -> models.Groups:
        logger.debug("Вызов функции перевода моделей групп в модель ответа")
        groups_by_institute_and_degree = {}

        for group in groups:
            if group.institute not in groups_by_institute_and_degree:
                groups_by_institute_and_degree[group.institute] = {}
            if group.degree not in groups_by_institute_and_degree[group.institute]:
                groups_by_institute_and_degree[group.institute][group.degree] = []
            groups_by_institute_and_degree[group.institute][group.degree].append(group.name)

        groups_list = []

        for institute, degrees in groups_by_institute_and_degree.items():
            groups_list.extend(
                models.GroupList(institute=institute, degree=degree, groups=groups)
                for degree, groups in degrees.items()
            )

        total = sum(len(groups.groups) for groups in groups_list)

        logger.debug(f"Обработка завершена. Общее число групп - {total}")
        return models.Groups(total=total, result=groups_list)
