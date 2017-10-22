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


def get_request(url, proxy=None):
    try:
        res = requests.get(url, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36'})
        return {'html': res.text, 'status': res.status_code, 'url': res.url, 'error': None, 'original_url': url}
    except requests.RequestException:
        return

