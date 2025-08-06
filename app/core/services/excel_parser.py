import asyncio
import logging
from concurrent.futures import ProcessPoolExecutor
from datetime import datetime
from pathlib import Path

import pandas as pd
from pandas import DataFrame

log = logging.getLogger(__name__)


class ExcelParser:
    async def parse_all_excel_files(self) -> list[list[dict[str, str | int]]]:
        paths = self._get_all_excel_files_name()
        loop = asyncio.get_running_loop()

        with ProcessPoolExecutor() as pool:
            tasks = [loop.run_in_executor(pool, self.parse_excel_file, path) for path in paths]
            return await asyncio.gather(*tasks)

    def parse_excel_file(self, file_path) -> list[dict[str, str | int]]:
        df = pd.read_excel(file_path)
        date = df.iloc[2, 1][-10:]
        start_row = self._get_start_row(df=df)
        all_data = self._get_all_data(start_row=start_row, df=df, date=date)
        return all_data

    @staticmethod
    def _get_start_row(df: DataFrame) -> int:
        start_row = 4
        while "Единица измерения: Метрическая тонна" != df.iloc[start_row, 1]:
            start_row += 1
        else:
            start_row += 3
        return start_row

    @staticmethod
    def _get_all_data(start_row: int, df: DataFrame, date: str) -> list[dict[str, str]]:
        all_data = list()

        while "Итого:" not in df.iloc[start_row, 1]:
            row = df.iloc[start_row]
            start_row += 1

            try:
                count = int(row.iloc[14])
            except ValueError:
                continue

            if count < 1:
                continue

            exchange_product_id = row.iloc[1]
            exchange_product_name = row.iloc[2]
            delivery_basis_name = row.iloc[3]

            data = {
                "exchange_product_id": exchange_product_id,
                "exchange_product_name": exchange_product_name,
                "oil_id": exchange_product_id[:4],
                "delivery_basis_id": exchange_product_id[4:7],
                "delivery_basis_name": delivery_basis_name,
                "delivery_type_id": exchange_product_id[-1],
                "volume": int(row.iloc[4]),
                "total": int(row.iloc[5]),
                "count": int(count),
                "date": datetime.strptime(date, "%d.%m.%Y").date(),
            }

            all_data.append(data)

        return all_data

    @staticmethod
    def _get_all_excel_files_name() -> list[str]:
        downloads_dir = Path(__file__).parent.parent.parent.parent / "downloads"
        excel_files = list(downloads_dir.glob("*.xls"))
        return excel_files
