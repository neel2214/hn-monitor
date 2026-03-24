# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
import time


class BiltuscraperPipeline:
    def process_item(self, item, spider):

        adapter = ItemAdapter(item)

        data_names = ['Score' , 'Comment_Count']
        for data_name in data_names:
            cleaned_data = adapter.get(data_name)
            data_array = cleaned_data.split()
            cleaned_data = data_array[0]
            adapter[data_name] = cleaned_data

        
        
        user = adapter.get('User_name')

        if user is None:
            adapter['Type'] ='Job Post'
        else:
            adapter['Type'] = 'News'    

        return item

import mysql.connector

class MySQLPipeline:
    def open_spider(self, spider):
        
        self.conn = mysql.connector.connect(
            host="hacker-news-scraper-mysql-hacker-news-scraper.i.aivencloud.com",
            port=26054, 
            user="avnadmin",
            password="AVNS_O-JyMlJ__uSoVpa3Uas",
            database="scraper",
            ssl_ca="ca.pem", 
            ssl_verify_cert=True
        )
        self.curr = self.conn.cursor(buffered=True)
        

        self.curr.execute("""
            CREATE TABLE IF NOT EXISTS hacker_news (
                id INT AUTO_INCREMENT PRIMARY KEY,
                header TEXT,
                news_link VARCHAR(512) UNIQUE,
                source VARCHAR(255),
                score INT,
                score_id VARCHAR(100),
                user_name VARCHAR(255),
                user_url VARCHAR(512),
                type VARCHAR(50),
                comment_count INT,
                scraped_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        try:
            
            self.curr.execute("DELETE FROM hacker_news WHERE scraped_at < NOW() - INTERVAL 1 DAY")
            self.conn.commit()
        except Exception as e:
            print(f"Cleanup error: {e}")
        
    
    def process_item(self, item, spider):

        header = item.get('Header')
        
        
        self.curr.execute("SELECT id FROM hacker_news WHERE header = %s", (header,))
        result = self.curr.fetchone()
        
        if result:
            spider.logger.info(f"Duplicate header found: {header}. Skipping...")
            return item 
        
        query = """
            INSERT IGNORE INTO hacker_news 
            (header, news_link, source, score, score_id, user_name, user_url, type, comment_count) 
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        
        
        score = item.get('Score', 0)
        comments = item.get('Comment_Count', 0)

        
        if str(comments).lower() == 'discuss' or not comments
            comments = 0

        values = (
            item.get('Header'),
            item.get('News_link'),
            item.get('Source'),
            int(item.get('Score', 0)),
            item.get('Score_id'),       
            item.get('User_name'),
            item.get('User_url'),        
            item.get('Type'),
            int(comments)
        )

        try:
            self.curr.execute(query, values)
            self.conn.commit()
        except Exception as e:
            print(f"Error saving to MySQL: {e}")
            
        return item
    

    def close_spider(self, spider):
        
        self.curr.close()
        self.conn.close()
        time.sleep(2)
            

        



