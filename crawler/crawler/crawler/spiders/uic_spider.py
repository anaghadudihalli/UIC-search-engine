# -*- coding: utf-8 -*-
import scrapy
from scrapy.linkextractors.lxmlhtml import LxmlLinkExtractor

from ..items import CrawlerItem
from scrapy.spiders import CrawlSpider, Rule
from bs4 import BeautifulSoup
from bs4.element import Comment


def tag_visible(element):
    if element.parent.name in ['style', 'script', 'head', 'title', 'meta', '[document]', 'footer', 'menu', 'img',
                               'form', 'input', 'noscript', 'svg', 'path']:
        return False
    if isinstance(element, Comment):
        return False
    return True


class UicSpiderSpider(CrawlSpider):
    count = 0
    name = 'uic_spider'
    allowed_domains = ['uic.edu']
    start_urls = ['https://cs.uic.edu/']
    custom_settings = {
        'DEPTH_PRIORITY': 5,
    }

    rules = [Rule(LxmlLinkExtractor(allow_domains=('uic.edu'), deny_domains=('login.uic.edu'), canonicalize=True),
                  callback='parse_data',
                  follow=True)]

    def parse_data(self, response):
        item = CrawlerItem()
        title = response.css("head title::text").extract_first().strip()

        # Extract page title
        if title.endswith(' | University of Illinois at Chicago'):
            title = title[:-36]
        soup = BeautifulSoup(response.text, "html.parser")
        for div in soup.find_all("div", {'class': 'browser-stripe'}):
            div.decompose()

        # Extract page content
        contents = soup.findAll(text=True)
        visible_texts = filter(tag_visible, contents)
        item['content'] = " ".join(t.strip() for t in visible_texts)

        outlinks = []
        le = LxmlLinkExtractor(allow_domains=('uic.edu'), deny_domains=('login.uic.edu'), unique=True,
                               canonicalize=True)
        for link in le.extract_links(response):
            outlinks.append(link.url)

        if title != 'UIC Directory' and 'uic.edu' in response.request.url:
            item['title'] = title
            item['url'] = response.request.url
            item['outlinks'] = outlinks
            yield item
