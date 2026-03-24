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
            stderr=subprocess.DEVNULL
        )
        return jsonify({
            "status": "success", 
            "message": "Scraper triggered in background"
        }), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# --- CRITICAL CHANGE FOR RENDER ---
if __name__ == '__main__':
    # Get port from environment or default to 5000
    port = int(os.environ.get("PORT", 5000))
    # host="0.0.0.0" is mandatory for Render/Docker to find the app
    app.run(host="0.0.0.0", port=port, debug=False, threaded=True)
