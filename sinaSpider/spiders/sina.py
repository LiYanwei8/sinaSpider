# -*- coding: utf-8 -*-
import scrapy
from sinaSpider.items import SinaspiderItem
import os

import sys
reload(sys)
sys.setdefaultencoding("utf-8")


class SinaSpider(scrapy.Spider):
    name = 'sina'
    allowed_domains = ['sina.com.cn']
    start_urls = ['http://sina.com.cn/']


    def parse(self, response):
        '''
        获取所有大类的Url和标题,子类的url和标题
        :param response:
        :return:
        '''
        items = []
        # 所有的大类的标题和url
        parentTitle = response.xpath('//div[@class="main-nav"]/div/ul/li[1]/a/b/text()').extract()
        parentUrls = response.xpath('//div[@class="main-nav"]/div/ul/li[1]/a/@href').extract()

        # 所有的子类的标题和url
        subTitle = response.xpath('//div[@class="main-nav"]/div/ul/li/a/text()').extract()
        subUrls = response.xpath('//div[@class="main-nav"]/div/ul/li[position()>1]/a/@href').extract()
        print subTitle, subUrls

        # 爬取所有大类
        for i in range(0, len(parentTitle)):
            # 指定大类目录的路径和目录名
            parentFilename = "./Data/" + parentTitle[i]

            # 如果目录不存在，则创建目录
            if (not os.path.exists(parentFilename)):
                os.makedirs(parentFilename)

            # 爬取所有小类
            for j in range(0, len(subUrls)):
                item = SinaspiderItem()

                # 保存大类的title和urls
                item['parentTitle'] = parentTitle[i]
                item['parentUrls'] = parentUrls[i]

                # 检查小类的url是否以同类别大类url开头，如果是返回True (sports.sina.com.cn 和 sports.sina.com.cn/nba)
                if_belong = subUrls[j].startswith(item['parentUrls'])

                # 如果属于本大类，将存储目录放在本大类目录下
                if (if_belong):
                    subFilename = parentFilename + '/' + subTitle[j]
                    # 如果目录不存在，则创建目录
                    if (not os.path.exists(subFilename)):
                        os.makedirs(subFilename)

                    # 存储 小类url、title和filename字段数据
                    item['subUrls'] = subUrls[j]
                    item['subTitle'] = subTitle[j]
                    item['subFilename'] = subFilename

                    items.append(item)
            # 发送每个小类url的Request请求，得到Response连同包含meta数据 一同交给回调函数 second_parse 方法处理
            for item in items:
                yield scrapy.Request(url=item['subUrls'],
                                     meta={'meta_1': item},
                                     callback=self.second_parse)


    def second_parse(self,response):
        '''
        对于返回的小类的url，再进行递归请求
        :return:
        '''
        pass
        # 提取每次Response的meta数据
        meta_1 = response.meta['meta_1']

        # 取出小类里所有子链接
        sonUrls = response.xpath('//a/@href').extract()
        print "进行递归请求"
        items = []
        for i in range(0, len(sonUrls)):
            # 检查每个链接是否以大类url开头、以.shtml结尾，如果是返回True
            if_belong = sonUrls[i].endswith('.shtml') and sonUrls[i].startswith(meta_1['parentUrls'])

            # 如果属于本大类，获取字段值放在同一个item下便于传输
            if (if_belong):
                item = SinaspiderItem()
                item['parentTitle'] = meta_1['parentTitle']
                item['parentUrls'] = meta_1['parentUrls']
                item['subUrls'] = meta_1['subUrls']
                item['subTitle'] = meta_1['subTitle']
                item['subFilename'] = meta_1['subFilename']
                item['sonUrls'] = sonUrls[i]
                items.append(item)

        # 发送每个小类下子链接url的Request请求，得到Response后连同包含meta数据 一同交给回调函数 detail_parse 方法处理
        for item in items:
            yield scrapy.Request(url=item['sonUrls'],
                                 meta={'meta_2': item},
                                 callback=self.detail_parse)


    def detail_parse(self, response):
        '''
        数据解析方法，获取文章标题和内容
        :param response:
        :return:
        '''
        item = response.meta['meta_2']
        content = ""
        head = response.xpath('//h1[@id=\"artibodyTitle\"]/text()')

        content_list = response.xpath('//div[@id=\"artibody\"]/p/text()').extract()
        # 将p标签里的文本内容合并到一起
        for content_one in content_list:
            content += content_one

        item['head'] = head
        item['content'] = content

        yield item

