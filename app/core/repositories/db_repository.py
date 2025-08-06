import logging
from abc import abstractmethod
from datetime import date

from sqlalchemy import insert, select, Select
from sqlalchemy.ext.asyncio import AsyncSession
from typing_extensions import Protocol

from app.api.api_v1.schemas import DynamicRequest, TradingResultsRequest
from app.core.database.models.spimex_trading_results import SpimexTradingResult

log = logging.getLogger(__name__)


class IDBRepository(Protocol):
    @abstractmethod
    async def create_doc(self, data: dict[str, str]) -> None:
        raise NotImplementedError

    @abstractmethod
    async def create_docs_bulk(self, data_list: list[dict[str, str]]) -> None:
        raise NotImplementedError

    @abstractmethod
    async def get_all_trading_dates(self, limit: int) -> list[date]:
        raise NotImplementedError

    @abstractmethod
    async def get_dynamics(self, request: DynamicRequest) -> list[SpimexTradingResult]:
        raise NotImplementedError

    @abstractmethod
    async def get_trading_results(
        self, request: TradingResultsRequest
    ) -> list[SpimexTradingResult]:
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

    async def get_all_trading_dates(self, limit: int) -> list[date]:
        query = (
            select(SpimexTradingResult.date)
            .group_by(SpimexTradingResult.date)
            .order_by(SpimexTradingResult.date.desc())
        )
        result = await self.session.scalars(query)
        return list(result)

    async def get_dynamics(self, request: DynamicRequest) -> list[SpimexTradingResult]:
        query = (
            select(SpimexTradingResult)
            .where(SpimexTradingResult.date.between(request.start_date, request.end_date))
            .order_by(SpimexTradingResult.date.desc())
        )

        query = await self._shared_filter_query(request=request, query=query)
        result = await self.session.scalars(query)
        return list(result)

    async def get_trading_results(
        self, request: TradingResultsRequest
    ) -> list[SpimexTradingResult]:
        query = (
            select(SpimexTradingResult)
            .where(SpimexTradingResult.oil_id == request.oil_id)
            .order_by(SpimexTradingResult.date.desc())
            .limit(1)
        )

        query = await self._shared_filter_query(request=request, query=query)
        result = await self.session.scalars(query)
        return list(result)

    @staticmethod
    async def _shared_filter_query(
            request: DynamicRequest | TradingResultsRequest,
            query: Select
    ) -> Select:

        if request.oil_id:
            query = query.where(SpimexTradingResult.oil_id == request.oil_id)
        if request.delivery_type_id:
            query = query.where(SpimexTradingResult.delivery_type_id == request.delivery_type_id)
        if request.delivery_basis_id:
            query = query.where(SpimexTradingResult.delivery_basis_id == request.delivery_basis_id)

        return query
