import scrapy
from biltuScraper.items import BiltuscraperItem

class BiltuspiderSpider(scrapy.Spider):
    name = "biltuSpider"
    allowed_domains = ["news.ycombinator.com"]
    start_urls = ["https://news.ycombinator.com/"]

    def parse(self, response):

        headers = response.css('tr.athing')
        infos = response.css('td.subtext')
        
        news_count = len(headers)
        

        

        for news in range(news_count):
                
                    current_header = headers[news]
                    current_info = infos[news]
                    

                    all_links = current_info.css('a::text').getall()
                    comments = all_links[-1] 


                    item = BiltuscraperItem()

                
                    item['Header'] = current_header.css('span.titleline a::text').get()
                    item['News_link'] = current_header.css('span.titleline a::attr(href)').get()
                    item['Source'] = current_header.css('span.sitestr::text').get()
                    item['Score'] = current_info.css('span.score::text').get()
                    item['Score_id'] = current_info.css('span.score::attr(id)').get()
                    item['User_name'] = current_info.css('a.hnuser::text').get()
                    item['User_url'] = current_info.css('a.hnuser::attr(href)').get()
                    item['Comment_Count'] = comments

                    yield item
        
        next_page = response.css('a.morelink::attr(href)').get()
        if next_page: # One request only!
            yield response.follow(next_page, callback=self.parse)
