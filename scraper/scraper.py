import asyncio
from collections import deque
from concurrent.futures import ThreadPoolExecutor
from random import choice

from aiohttp import web

from common.request import post_request, get_request


class Scraper:

    def __init__(self, host, port, parser_endpoints):

        self.host = host
        self.port = port
        self.pool = ThreadPoolExecutor(max_workers=20)
        self.loop = asyncio.get_event_loop()
        self.urls_to_parser = deque([])
        self.parser_endpoints = parser_endpoints

    def scrape_callback(self, return_value):
        return_value = return_value.result()
        if return_value:
            self.urls_to_parser.append(return_value)

    async def get_urls(self, request):
        data = await request.json()
        url = data.get('url')
        if url:
            t = self.loop.run_in_executor(self.pool, get_request, url)
            t.add_done_callback(self.scrape_callback)
        return web.json_response({'Status': 'Dispatched'})

    async def process_queue(self):
        while True:
            if self.urls_to_parser:
                data_to_post = self.urls_to_parser.popleft()
                print('Sending URL to dispatcher')
                selected_host = choice(self.parser_endpoints)
                res = await post_request(selected_host, data_to_post)
            else:
                await asyncio.sleep(0.1)

    async def start_background_tasks(self, app):
        app['dispatch'] = app.loop.create_task(self.process_queue())

    async def cleanup_background_tasks(self, app):
        app['dispatch'].cancel()
        await app['dispatch']

    async def create_app(self, loop):
        app = web.Application()
        app.router.add_post('/', self.get_urls)
        return app

    def run_app(self):
        loop = self.loop
        app = loop.run_until_complete(self.create_app(loop))
        app.on_startup.append(self.start_background_tasks)
        app.on_cleanup.append(self.cleanup_background_tasks)
        web.run_app(app, host=self.host, port=self.port)


if __name__ == '__main__':
    s = Scraper(host='127.0.0.1', port=5002, parser_endpoints=['http://127.0.0.1:5003/'])
    s.run_app()