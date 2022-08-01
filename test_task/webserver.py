import asyncio

from aiohttp import web
from aiohttp.web_request import Request

from databases.repository import Repository
from databases.shelvedb import ShelveDB
from test_task import Parser

import aiohttp_jinja2
import jinja2


class WebServer(web.Application):
    repository: Repository

    def __init__(self):
        super().__init__()
        self.__init_repository()
        self.on_startup.append(self.__run_parser_task)
        self.on_cleanup.append(self.__stop_parser_task)
        self.router.add_get('/', self.main)
        self.router.add_get('/{filter}', self.main)
        self.__init_jinja()

    def __init_repository(self):
        """
        Init databases
        :return:
        """
        self.repository = ShelveDB()

    def __init_jinja(self):
        aiohttp_jinja2.setup(self,
                             loader=jinja2.FileSystemLoader('test_task/static'))

    @staticmethod
    async def __run_parser_task(app):
        """
        Add parser task to background tasks
        :param app: application instance
        :return:
        """
        app['parser'] = asyncio.create_task(Parser().run())

    @staticmethod
    async def __stop_parser_task(app):
        """
        Rm parser task before stopping
        :param app: application instance
        :return:
        """
        app['parser'].cancel()
        await app['parser']

    async def main(self, request: Request):
        """
        Base end-point
        :param request: client request
        :return:
        """
        limit = 10
        offset = 0
        if request.body_exists:
            body = await request.json()
            limit = body.get("limit", limit)
            offset = body.get("offset", offset)
        _filter = request.match_info.get('filter', "")
        data = self.repository.get(limit=limit, offset=offset, _filter=_filter)
        return aiohttp_jinja2.render_template("index.html",
                                              request,
                                              {'data': data})

    def run(self):
        """
        Run webserver
        :return:
        """
        web.run_app(self, port=8000)
