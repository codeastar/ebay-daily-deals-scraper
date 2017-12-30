# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class EBayItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    name = scrapy.Field()
    category = scrapy.Field()
    link = scrapy.Field()
    img_path = scrapy.Field()        
    currency = scrapy.Field()   
    price = scrapy.Field()   
    orignal_price = scrapy.Field()   
