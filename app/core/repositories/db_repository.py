import logging
from abc import abstractmethod

from sqlalchemy import insert
from sqlalchemy.ext.asyncio import AsyncSession
from typing_extensions import Protocol

from app.core.db.models.spimex_trading_results import SpimexTradingResult

log = logging.getLogger(__name__)


class IDBRepository(Protocol):
    @abstractmethod
    async def create_doc(self, data: dict[str, str]) -> None:
        raise NotImplementedError

    @abstractmethod
    async def create_docs_bulk(self, data_list: list[dict[str, str]]) -> None:
        raise NotImplementedError


class AlchemyRepository(IDBRepository):
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create_doc(self, data: dict[str, str | int]) -> None:
        trade_model = SpimexTradingResult(**data)
        self.session.add(trade_model)
        await self.session.commit()
        log.info("Файл успешно сохранен в БД!")

    async def create_docs_bulk(self, data_list: list[dict[str, str | int]]) -> None:
        await self.session.execute(insert(SpimexTradingResult), data_list)
        await self.session.commit()
