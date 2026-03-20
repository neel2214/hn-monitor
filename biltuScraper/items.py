# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class BiltuscraperItem(scrapy.Item):

    Header = scrapy.Field()
    News_link = scrapy.Field()
    Source = scrapy.Field()
    Score = scrapy.Field()
    Score_id = scrapy.Field()
    User_name = scrapy.Field()  
    User_url = scrapy.Field()
    Comment_Count = scrapy.Field()
    Type = scrapy.Field()
    pass
