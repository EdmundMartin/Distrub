import lxml.html as lh
from urllib.parse import urljoin


def get_all_links(crawled_url, original_url, html):
    found_urls = []
    dom = lh.fromstring(html)
    for href in dom.xpath('//a/@href'):
        url = urljoin(crawled_url, href)
        if url.startswith(original_url):
            found_urls.append(url)
    return found_urls