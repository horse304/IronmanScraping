# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy

class RaceResultItem(scrapy.Item):
    bib = scrapy.Field()
    name = scrapy.Field()
    gender = scrapy.Field()
    country = scrapy.Field()
    age_group = scrapy.Field()
    point = scrapy.Field()
    overall_rank = scrapy.Field()
    group_rank = scrapy.Field()
    gender_rank = scrapy.Field()
    time_overall = scrapy.Field()
    time_swim = scrapy.Field()
    time_bike = scrapy.Field()
    time_run = scrapy.Field()
    time_T1 = scrapy.Field()
    time_T2 = scrapy.Field()
    link = scrapy.Field()
    certificate = scrapy.Field()
