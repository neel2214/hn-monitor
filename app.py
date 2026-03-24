from flask import Flask, render_template, jsonify
import subprocess
import mysql.connector
import os

app = Flask(__name__)

def get_data_from_aiven():
    try:
        db = mysql.connector.connect(
            host="hacker-news-scraper-mysql-hacker-news-scraper.i.aivencloud.com",
            port=26054,
            user="avnadmin",
            password="AVNS_O-JyMlJ__uSoVpa3Uas",
            database="scraper",
            ssl_ca="ca.pem"  # Ensure this file is in your root folder
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
        # Popen starts the process and returns immediately
        subprocess.Popen(
            ["scrapy", "crawl", "biltuSpider", "--nolog"], 
            stdout=subprocess.DEVNULL, 
            stderr=subprocess.DEVNULL
        )
        return jsonify({
            "status": "success", 
            "message": "Scraper triggered in background"
        }), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    # threaded=True allows background tasks to run without freezing the UI
    app.run(debug=True, threaded=True)
