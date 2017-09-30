import asyncio
from collections import deque
from random import choice

from aiohttp import web

from common.request import post_request

class Dispatcher:

    SCRAPER_HOSTS = ['http://127.0.0.1:5002']

    def __init__(self, host, port):

        self.host = host
        self.port = port
        self.urls_to_dispatch = deque([])
        self.urls_crawled = set()
        self.loop = asyncio.get_event_loop()

    async def dispatch_queue(self, request):
        data = await request.json()
        for url in data.get('urls'):
            async with asyncio.BoundedSemaphore(1):
                url_item = url.get('url')
                if url_item not in self.urls_crawled:
                    self.urls_to_dispatch.append(url)
        return web.json_response({'Status': 'Dispatched'})

    async def process_queue(self):
        while True:
            if self.urls_to_dispatch:
                url_data = self.urls_to_dispatch.popleft()
                print(self.urls_to_dispatch)
                url_item = url_data.get('url')
                self.urls_crawled.add(url_item)
                selected_host = choice(self.SCRAPER_HOSTS)
                res = await post_request(selected_host, url_data)
            else:
                await asyncio.sleep(1)

    async def start_background_tasks(self, app):
        app['dispatch'] = app.loop.create_task(self.process_queue())

    async def cleanup_background_tasks(self, app):
        app['dispatch'].cancel()
        await app['dispatch']

    async def create_app(self, loop):
        app = web.Application()
        app.router.add_post('/', self.dispatch_queue)
        app.on_startup.append(self.start_background_tasks)
        app.on_cleanup.append(self.cleanup_background_tasks)
        return app

    def run_app(self):
        loop = self.loop
        app = loop.run_until_complete(self.create_app(loop))
        web.run_app(app, host=self.host, port=self.port)

if __name__ == '__main__':
    s = Dispatcher(host='127.0.0.1', port=5001)
    s.run_app()