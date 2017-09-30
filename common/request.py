import aiohttp
import requests

async def post_request(url, json, proxy=None):
    async with aiohttp.ClientSession() as client:
        try:
            async with client.post(url, json=json, proxy=proxy, timeout=60) as response:
                html = await response.text()
                return {'html': html, 'status': response.status, 'error': None}
        except aiohttp.ClientError as err:
            return {'error': err}


async def get_request(url, proxy=None):
    async with aiohttp.ClientSession() as client:
        try:
            async with client.post(url, proxy=proxy, timeout=60) as response:
                html = await response.text()
                return {'html': html, 'status': response.status, 'error': None, 'url': str(response.url),
                        'original_url': url}
        except aiohttp.ClientError as err:
            return {'error': err}

