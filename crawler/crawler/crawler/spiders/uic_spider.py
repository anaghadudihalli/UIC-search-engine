# -*- coding: utf-8 -*-
import scrapy
from scrapy.linkextractors.lxmlhtml import LxmlLinkExtractor

from ..items import CrawlerItem
from scrapy.spiders import CrawlSpider, Rule


class UicSpiderSpider(CrawlSpider):
    count = 0
    name = 'uic_spider'
    allowed_domains = ['uic.edu']
    start_urls = ['https://cs.uic.edu/']
    custom_settings = {
        'DEPTH_PRIORITY': 5,
    }

    rules = [Rule(LxmlLinkExtractor(allow_domains=('uic.edu'), deny_domains=('login.uic.edu')), callback='parse_data',
                  follow=True)]

    def parse_data(self, response):
        data = ''
        item = CrawlerItem()
        title = response.css("head title::text").extract_first().strip()
        if title.endswith(' | University of Illinois at Chicago'):
            title = title[:-36]
        content = response.css("p::text").extract()
        print(content)
        for string in content:
            if len(string.strip()) > 2 and string.strip() != 'We recommend using the latest version of IE11, Edge, Chrome, Firefox or Safari.' and 'Copyright' not in string.strip():
                data += string.strip() + ' '
        outlinks = []
        le = LxmlLinkExtractor(allow_domains=('uic.edu'), deny_domains=('login.uic.edu'), unique=True)
        for link in le.extract_links(response):
            outlinks.append(link.url)

        item['title'] = title
        item['url'] = response.request.url
        item['content'] = data
        item['outlinks'] = str(outlinks)
        yield item
