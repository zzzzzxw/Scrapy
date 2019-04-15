# -*- coding: utf-8 -*-
import time

import scrapy
from scrapy import Request
from housedata.items import HousedataItem


class DataspiderSpider(scrapy.Spider):
    name = 'dataSpider'
    allowed_domains = ['cd.lianjia.com']
    start_urls = ['https://cd.fang.lianjia.com/loupan/']

    def parse(self, response):
        total = response.xpath('//div[@class="page-box"]/@data-total-count').extract_first()
        total = int(int(total)/10)
        for i in range(1, total + 1):
            url = 'https://cq.fang.lianjia.com/loupan/pg{}/'.format(i)
            yield Request(url, callback=self.parsePage, dont_filter=True)

    def parsePage(self, response):
        loupan_urls = response.xpath('//ul[@class="resblock-list-wrapper"]//li/a/@href').extract()
        for loupan in loupan_urls:
            loupan_url = response.urljoin(loupan)
            yield Request(loupan_url, callback=self.parseDetails, dont_filter=True)
            time.sleep(1)

    def parseDetails(self, response):
        houseData = HousedataItem()
        try:
            houseData['name'] = response.xpath('//div[@class="name-box"]/a/@title').extract_first()
            tag = response.xpath('//p[@class="jiage"]/span/text()').extract_first()
            if tag=='均价':
                junjia = response.xpath('//p[@class="jiage"]/span[@class="junjia"]/text()').extract_first()
                danwei = response.xpath('//p[@class="jiage"]/span[@class="yuan"]/text()').extract_first()
                price = junjia + danwei
            else:
                price=tag
            houseData['keyWords'] = response.xpath('//div[@class="bottom-info"]/p[1]//span/text()').extract()
            houseData['location'] = response.xpath('//div[@class="bottom-info"]/p[3]/span/text()').extract_first()

            houseData['price'] = price
            '''
            houseData = {'name': str(name), 
                         'prices': prices, 
                         'keyWords': key_words, 
                         'locationName': location_name
                         }
                         '''
            yield houseData
        except Exception as e:
            print(e)
        # print(houseData)
