import logging
import time

from app.core.repositories.db_repository import IDBRepository
from app.core.excel_parser import ExcelParser
from app.core.parser import Parser
from app.core.settings import Settings

log = logging.getLogger(__name__)


class Service:
    def __init__(
        self,
        settings: Settings,
        parser: Parser,
        excel_parser: ExcelParser,
        db_repository: IDBRepository,
    ) -> None:
        self.parser = parser
        self.settings = settings
        self.excel_parser = excel_parser
        self.db_repository = db_repository

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