import asyncio
from collections import deque
from concurrent.futures import ProcessPoolExecutor
from random import choice
from threading import BoundedSemaphore

from aiohttp import web

from common.request import post_request
from common.parser import get_all_links


class Parser:

    def __init__(self, host, port, dispatcher_endpoints):

        self.host = host
        self.port = port
        self.pool = ProcessPoolExecutor(max_workers=5)
        self.loop = asyncio.get_event_loop()
        self.urls_to_dispatcher = deque([])
        self.urls_already_discovered = set()
        self.dispatcher_endpoints = dispatcher_endpoints
        self.semaphore = BoundedSemaphore(value=1)

    def parser_callback(self, urls):
        urls = urls.result()
        if urls:
            for url in urls:
                with self.semaphore:
                    if url not in self.urls_already_discovered:
                        self.urls_to_dispatcher.append(url)
                        self.urls_already_discovered.add(url)

    async def get_responses(self, request):
        data = await request.json()
        crawled_url, o_url, html = data.get('url'), data.get('original_url'), data.get('html')
        t = self.loop.run_in_executor(self.pool, get_all_links, crawled_url, o_url, html)
        t.add_done_callback(self.parser_callback)
        return web.json_response({'Status': 'Dispatched'})

    async def process_queue(self):
        while True:
            if self.urls_to_dispatcher:
                url = self.urls_to_dispatcher.popleft()
                print('Sending URL to dispatcher')
                selected_host = choice(self.dispatcher_endpoints)
                data_to_post = {'urls': [{'url': url}]}
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
        app.router.add_post('/', self.get_responses)
        app.on_startup.append(self.start_background_tasks)
        app.on_cleanup.append(self.cleanup_background_tasks)
        return app

    def run_app(self):
        loop = self.loop
        app = loop.run_until_complete(self.create_app(loop))
        web.run_app(app, host=self.host, port=self.port)

if __name__ == '__main__':
    p = Parser('127.0.0.1', 5003, dispatcher_endpoints=['http://127.0.0.1:5001/'])
    p.run_app()