import asyncio
import logging
import os
from itertools import chain
from urllib.parse import urljoin

import aiofiles
from aiohttp import ClientError, ClientSession
from bs4 import BeautifulSoup

from app.core.settings import Settings

log = logging.getLogger(__name__)


class Parser:
    def __init__(self, settings: Settings, session: ClientSession) -> None:
        self.session = session
        self.settings = settings

    async def downland_excel_files(self) -> None:
        urls = [f"{self.settings.links.url}{str(page)}" for page in range(1, 65)]
        tasks = [asyncio.create_task(self.parse_page(url=url)) for url in urls]
        responses = await asyncio.gather(*tasks)
        soups = [self.get_soup(response=response) for response in responses]
        doc_urls = list(chain.from_iterable(self.get_docs_links(soup=soup) for soup in soups))
        tasks = [asyncio.create_task(self.download_file(url=url)) for url in doc_urls]
        await asyncio.gather(*tasks)

    # def get_next_page(self, soup: BeautifulSoup) -> str:
    #     next_page = soup.find("li", class_="bx-pag-next").find("a")["href"]
    #     next_page = urljoin(self.settings.links.domain, next_page)
    #     return next_page

    async def parse_page(self, url: str) -> str:
        try:

            async with self.session.get(url=url, timeout=15) as response:
                response.raise_for_status()
                return await response.text()

        except asyncio.TimeoutError:
            log.error("Время вышло по запросу %s", url)
        except ClientError as e:
            log.error("HTTP error while fetching %s: %s", url, e)
        except Exception as e:
            log.error("Неизвестная ошибка: %s", e.__class__.__name__)

    def get_soup(self, response: str) -> BeautifulSoup:
        return BeautifulSoup(response, self.settings.links.parse_method)

    def get_docs_links(self, soup: BeautifulSoup) -> list[str]:
        divs = soup.find_all("div", class_="accordeon-inner__wrap-item")[:10]
        links = list()

        for div in divs:
            date = div.find("span").text
            if int(date[-4:]) > 2022:
                url = urljoin(self.settings.links.domain, div.find("a")["href"])
                links.append(url)

        return links

    async def download_file(self, url: str, folder: str = "downloads") -> str:
        os.makedirs(folder, exist_ok=True)
        filename = os.path.join(folder, url.split("/")[-1].split("?")[0])

        async with self.session.get(url) as response:
            response.raise_for_status()

            async with aiofiles.open(filename, "wb") as f:
                await f.write(await response.read())

        log.info(f"Файл сохранен: {filename}")
        return filename
