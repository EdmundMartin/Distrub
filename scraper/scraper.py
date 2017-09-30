import asyncio
from collections import deque
from concurrent.futures import ThreadPoolExecutor
from random import choice

from aiohttp import web

from common.request import post_request, get_request


class Scraper:

    PARSER_ENDPOINTS = ['http://127.0.0.1:5003']

    def __init__(self, host, port):

        self.host = host
        self.port = port
        self.pool = ThreadPoolExecutor(max_workers=20)
        self.loop = asyncio.get_event_loop()
        self.urls_to_parser = deque([])
        self.count = 0

    def scrape_callback(self, return_value):
        return_value = return_value.result()
        if return_value:
            self.urls_to_parser.append(return_value)

    async def get_urls(self, request):
        data = await request.json()
        url = data.get('url')
        if url:
            result_json = await get_request(url)
            res = await post_request(choice(self.PARSER_ENDPOINTS), json=result_json)
            print(res)
        return web.json_response({'Status': 'Dispatched'})

    async def create_app(self, loop):
        app = web.Application()
        app.router.add_post('/', self.get_urls)
        return app

    def run_app(self):
        loop = self.loop
        app = loop.run_until_complete(self.create_app(loop))
        web.run_app(app, host=self.host, port=self.port)


if __name__ == '__main__':
    s = Scraper(host='127.0.0.1', port=5002)
    s.run_app()