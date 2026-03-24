from flask import Flask, render_template, jsonify
import subprocess
import mysql.connector
import os
import threading
import requests
import time

app = Flask(__name__)

def keep_alive():
    """Pings the server every 10 minutes to prevent Render sleep."""
    while True:
        try:

            requests.get("http://127.0.0.1:5000/health")
        except:
            pass
        time.sleep(600) 

@app.route('/health')
def health():
    return "Alive", 200


def get_data_from_aiven():
    try:
        db = mysql.connector.connect(
            host="hacker-news-scraper-mysql-hacker-news-scraper.i.aivencloud.com",
            port=26054,
            user="avnadmin",
            password="AVNS_O-JyMlJ__uSoVpa3Uas",
            database="scraper",
            ssl_ca="ca.pem" 
        )
        cursor = db.cursor(dictionary=True, buffered=True)        
        cursor.execute("SELECT * FROM hacker_news ORDER BY scraped_at DESC")
        rows = cursor.fetchall()
        db.close()
        return rows
    except Exception as e:
        print(f"Database Error: {e}")
        return []

@app.route('/')
def home():
    news_data = get_data_from_aiven()
    return render_template('index.html', news=news_data)

@app.route('/trigger-scrape', methods=['GET', 'POST'])
def trigger_scrape():
    try:

        subprocess.Popen(
            ["scrapy", "crawl", "biltuSpider", "--nolog"], 
            stdout=subprocess.DEVNULL, 
            stderr=subprocess.DEVNULL,
            start_new_session=True 
        )

        return jsonify({"s": "ok"}), 202
    except Exception as e:
        return jsonify({"e": str(e)}), 500

if __name__ == '__main__':  
    
    if os.environ.get("RENDER") or not os.environ.get("DEBUG"):
        threading.Thread(target=keep_alive, daemon=True).start()
        
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False, threaded=True)
