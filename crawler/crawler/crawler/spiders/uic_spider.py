# -*- coding: utf-8 -*-
import scrapy
from ..items import CrawlerItem
from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor


class UicSpiderSpider(CrawlSpider):
    count = 0
    name = 'uic_spider'
    allowed_domains = ['uic.edu']
    start_urls = ['https://cs.uic.edu/']
    custom_settings = {
        'DEPTH_PRIORITY': 5,
    }

    rules = [Rule(LinkExtractor(allow=('uic.edu'), deny=('login.uic.edu')), callback='parse_data', follow=True)]

    def parse_data(self, response):
        data = ''
        item = CrawlerItem()
        title = response.css("head title::text").extract_first().strip()
        content =response.css("p::text").extract()
        print(content)
        for string in content:
            if len(string.strip()) > 2 and string.strip() != 'We recommend using the latest version of IE11, Edge, Chrome, Firefox or Safari.' and 'Copyright' not in string.strip():
                data += string.strip() + ' '
        item['title'] = title
        item['url'] = response.request.url
        item['content'] = data
        yield item

