"""Contains template code for model repositories."""

from re import compile
from typing import Any, Dict
from sqlalchemy import select, insert, update, delete
from sqlalchemy.sql.expression import literal_column
from sqlalchemy.engine.result import exc
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
from sqlalchemy import Sequence

from .base import AbstractRepository
from ..utils.app_loggers import get_logger


class SQLAlchemyRepository(AbstractRepository):
    model = None
    model_name = None
    logger = get_logger(__name__)

    @staticmethod
    def _get_error_message_on_conflict(
        err: IntegrityError,
    ) -> tuple[str, str] | None:
        """
        Parses the IntegrityError message and returns tuple with conflicting field name and value.
        """
        pattern = compile(r"DETAIL\:\s+Key \((?P<field>.+?)\)=")
        match = pattern.search(str(err))
        if match is not None:
            return match["field"], "Violation of the unique constraint!"

    async def add_one(
        self, data: dict, session: AsyncSession
    ) -> Dict | tuple[str, str, str] | None:
        stmt = insert(self.model).values(**data).returning(literal_column("*"))
        try:
            result = await session.execute(stmt)
            await session.commit()
            result = dict(result.mappings().first().items())
            self.logger.info(
                f"A new {self.model_name} with id={result['id']} was created in the database."
            )
            return result
        except IntegrityError as exc:
            error_message = self._get_error_message_on_conflict(exc)
            return error_message

    async def find_one(
        self, session: AsyncSession, id: int | None, email: str | None = None
    ) -> Dict | None:
        if isinstance(id, int):
            stmt = select(self.model).filter_by(id=id)
        elif isinstance(email, str):
            stmt = select(self.model).filter_by(email=email)
        else:
            return None
        result = await session.execute(stmt)
        try:
            result = dict(result.mappings().first().items())[self.model_name]
            self.logger.info(
                f"The {self.model_name} with id={result.id} was SELECTED from the database."
            )
            result = result.__dict__
            del result["_sa_instance_state"]
            return result
        except AttributeError as e:
            return None

    async def find_all(self, session: AsyncSession) -> Sequence[Any]:
        stmt = select(self.model)
        result = await session.execute(stmt)
        self.logger.info(f"All {self.model_name}s were SELECTED from the db.")
        return result.scalars().all()

    async def delete_one(self, id: int, session: AsyncSession) -> int | None:
        stmt = delete(self.model).where(self.model.id == id).returning(self.model.id)
        result = await session.execute(stmt)
        try:
            await session.commit()
            result = result.scalar_one()
            self.logger.info(
                f"A {self.model_name} with id={id} was DELETED from the database."
            )
            return result
        except exc.NoResultFound:
            return None

    async def update_one(
        self, id: int, data: dict, session: AsyncSession
    ) -> Dict | tuple | None:
        stmt = (
            update(self.model)
            .where(self.model.id == id)
            .values(**data)
            .returning(literal_column("*"))
        )
        try:
            try:
                result = await session.execute(stmt)
                await session.commit()
                result = dict(result.mappings().first().items())
                self.logger.info(
                    f"A {self.model_name} with id={result['id']} was UPDATED in the database."
                )
                return result
            except IntegrityError as exc:
                error_message = self._get_error_message_on_conflict(exc)
                return error_message
        except AttributeError as e:
            return None
