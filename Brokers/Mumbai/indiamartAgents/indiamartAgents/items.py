# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class IndiamartagentsItem(scrapy.Item):
    description = scrapy.Field()
    locality = scrapy.Field()
    phone_no = scrapy.Field()
    company_name = scrapy.Field()
    city = scrapy.Field()
    scraped_time = scrapy.Field()
