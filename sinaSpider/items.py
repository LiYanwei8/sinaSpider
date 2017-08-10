# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class SinaspiderItem(scrapy.Item):
    # 大类标题,url
    parentTitle = scrapy.Field()
    parentUrls = scrapy.Field()

    # 小类的标题和子url
    subTitle = scrapy.Field()
    subUrls = scrapy.Field()

    # 小类目录存储路径
    subFilename = scrapy.Field()

    # 小类下的子链接
    sonUrls = scrapy.Field()

    # 文章的标题和内容
    head = scrapy.Field()
    content = scrapy.Field()