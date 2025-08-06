import json
import logging
import time
from datetime import date

from app.api.api_v1.schemas import DynamicRequest, TradingResultsRequest
from app.core.repositories.cache_repository import ICacheRepository
from app.core.repositories.db_repository import IDBRepository
from app.core.services.excel_parser import ExcelParser
from app.core.services.http_parser import Parser
from app.core.settings import Settings

log = logging.getLogger(__name__)


class Service:
    def __init__(
        self,
        settings: Settings,
        parser: Parser,
        excel_parser: ExcelParser,
        db_repository: IDBRepository,
        cache_repository: ICacheRepository,
    ) -> None:
        self.parser = parser
        self.settings = settings
        self.excel_parser = excel_parser
        self.db_repository = db_repository
        self.cache_repository = cache_repository

    async def load_docs_in_db(self) -> None:
        start = time.time()
        await self.parser.downland_excel_files()
        all_data = await self.excel_parser.parse_all_excel_files()
        log.info("Данные успешно собранны из файлов")
        total_result = 0

        for data in all_data:
            await self.db_repository.create_docs_bulk(data_list=data)
            total_result += (amount_rows := len(data))
            log.info("Сохранено %d записей", amount_rows)

        log.info(
            "Все данные успешно загрузились в БД за %.2f сек. Всего %d записей",
            time.time() - start,
            total_result,
        )

    async def get_last_trading_dates(self, limit: int) -> list[date]:
        """
        Список дат последних торговых дней (фильтрация по кол-ву последних торговых дней).
        """
        if cached := await self.cache_repository.get_cached_data(key=self.settings.redis.dates_key):
            dates = [date.fromisoformat(d) for d in cached]
            return dates[:limit]

        dates = await self.db_repository.get_all_trading_dates(limit=limit)
        serialized = json.dumps([d.isoformat() for d in dates])
        await self.cache_repository.set_cached_data(
            data=serialized, key=self.settings.redis.dates_key
        )
        return dates[:limit]

    async def get_dynamics(self, request: DynamicRequest):
        """
        список торгов за заданный период
        (фильтрация по oil_id, delivery_type_id, delivery_basis_id, start_date, end_date).
        """
        result = await self.db_repository.get_dynamics(request=request)
        return result

    async def get_trading_results(self, request: TradingResultsRequest):
        """
        список последних торгов (фильтрация по oil_id, delivery_type_id, delivery_basis_id)
        """
        result = await self.db_repository.get_trading_results(request=request)
        return result
