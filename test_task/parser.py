import asyncio
import time
from concurrent.futures import ThreadPoolExecutor
from functools import lru_cache
from typing import Dict

import aiohttp
from aiohttp import ClientResponse
from loguru import logger

from config import URL
from databases.shelvedb import ShelveDB
from .types import Result
from .utils import *
from databases.repository import Repository


class Parser:
    queue: asyncio.Queue[list[Result]] = asyncio.Queue(maxsize=10)
    repository: Repository
    time_for_repeat_fetch: int = 600  # Seconds

    @staticmethod
    async def __handle_response(resp: ClientResponse) -> Dict:
        """
        Check response on status code and return data
        or call exception
        :param resp: response from get request
        :return:
        """
        if resp.ok:
            data = await resp.json()
            return data
        else:
            err = "Unfounded error with status code %s\nText: %s" % (resp.status, await resp.json())
            raise CustomCodeException(err)

    @lru_cache()
    async def __fetch(self) -> None:
        """
        Create fetch. Put result to queue
        :return: None
        """
        while True:
            try:
                url = URL % int(time.time())
                async with aiohttp.ClientSession() as session:
                    async with session.post(url) as resp:
                        data: Dict = await self.__handle_response(resp)
                        data: list[Result] = FilterOutData(data=data)
                        await self.queue.put(data)
                logger.info(data)
                await asyncio.sleep(self.time_for_repeat_fetch)

            except (CustomCodeException, EventsNotFounded) as e:
                logger.error(e)
                return

            except Exception as e:
                logger.exception(e)
                return

    async def __save(self) -> None:
        """
        Asyncio task for saving data
        :return: None
        """
        loop = asyncio.get_running_loop()
        executor = ThreadPoolExecutor(1)
        while True:
            data: list[Result] = await self.__get_data_from_queue(self.queue)
            loop.run_in_executor(executor, self.repository.save, data)
            await asyncio.sleep(self.time_for_repeat_fetch)

    async def __get_data_from_queue(self, queue: asyncio.Queue) -> list[Result]:
        """
        Getting data from queue
        :param queue: selected queue with data
        :return: list with Result
        """
        data: list[Result] = await queue.get()
        self.queue.task_done()
        return data

    async def __init_repository(self) -> None:
        """
        Init repository instance
        :return: None
        """
        self.repository = ShelveDB()

    async def run(self) -> None:
        """
        Start initialization instances and creating tasks
        :return:
        """
        await self.__init_repository()
        save_task = asyncio.create_task(self.__save())
        fetch_task = asyncio.create_task(self.__fetch())
        tasks = (save_task, fetch_task,)
        await asyncio.wait(tasks, return_when=asyncio.FIRST_COMPLETED)

    def start(self) -> None:
        """
        Run parser with 'asyncio run'
        :return: None
        """
        asyncio.run(self.run())
