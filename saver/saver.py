import asyncio
import aiohttp
from aiohttp import web
from motor import motor_asyncio

class Saver:

    def __init__(self, host, port, mongo_url, mongo_db, mongo_collection):

        self.host = host
        self.port = port
        self.loop = asyncio.get_event_loop()

        self.mongo_client = motor_asyncio.AsyncIOMotorClient(mongo_url)
        self.database = self.mongo_client[mongo_db]
        self.collection = self.database[mongo_collection]

    async def get_items_to_save(self, request):
        data = await request.json()
        results = data.get('results')
        for result in results:
            insertion = await self.collection.insert_one(data)
        return web.json_response({'Success': 'Saved data'})

    async def create_app(self, loop):
        app = web.Application()
        app.router.add_post('/', self.get_items_to_save)
        return app

    def run_app(self):
        loop = self.loop
        app = loop.run_until_complete(self.create_app(loop))
        web.run_app(app, host=self.host, port=self.port)

if __name__ == '__main__':
    s = Saver('127.0.0.1', 5009, mongo_url='mongodb://localhost:27017', mongo_collection='vox',
                             mongo_db='vox_headlines')
    s.run_app()