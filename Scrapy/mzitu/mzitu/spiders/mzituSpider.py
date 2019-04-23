# -*- coding: utf-8 -*-
import time

import scrapy
from scrapy import Request
import re

from mzitu.items import MzituItem


class MzituSpider(scrapy.Spider):
    name = 'mzituSpider'
    allowed_domains = ['mzitu.com']
    start_urls = ['http://mzitu.com/all/']

    def parse(self, response):
        urls = response.xpath('//ul[@class="archives"]/li/p/a/@href').extract()
        print(len(urls))
        for i in urls[510:]:
            yield Request(i, callback=self.parsePage, dont_filter=True)
            time.sleep(3)

    def parsePage(self, response):
        try:
            img_srcs = []
            img_data = MzituItem()
            title = response.xpath('//h2[@class="main-title"]/text()').extract_first()
            img_src = response.xpath('//div[@class="main-image"]/p/a/img/@src').extract_first()
            total = response.xpath('//div[contains(@class,"pagenavi")]/a[last()-1]/span/text()').extract_first()
            str1 = img_src.rsplit('0', 1)[0]
            for i in range(1, int(total) + 1):
                if i < 10:
                    i = '0' + str(i) + '.jpg'
                    next_img = str1 + i
                else:
                    next_img = str1 + str(i)+ '.jpg'
                img_srcs.append(next_img)
            img_data['title'] = title
            img_data['img_list'] = img_srcs
            yield img_data

        except Exception as e:
            print(e)
