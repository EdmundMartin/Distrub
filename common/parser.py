import lxml.html as lh
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup


def get_all_links(crawled_url, original_url, html):
    found_urls = []
    dom = lh.fromstring(html)
    parsed = urlparse(original_url)
    original_url = '{}://{}'.format(parsed.scheme, parsed.netloc)
    for href in dom.xpath('//a/@href'):
        url = urljoin(crawled_url, href)
        if url.startswith(original_url):
            found_urls.append(url)
    return found_urls

def get_page_info(crawled_url, original_url, html):
    res_dict = {'crawled_url': crawled_url}

    try:
        soup = BeautifulSoup(html, 'lxml')
        title = soup.find('title')
        if title:
            title = title.get_text()
            res_dict.update({'title': title})

        h1 = soup.find('h1')
        if h1:
            h1 = h1.get_text()
            res_dict.update({'h1': h1})

        return res_dict
    except Exception as e:
        return {'crawled_url': crawled_url}