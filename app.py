from flask import Flask, render_template, jsonify
import subprocess
import mysql.connector
import os
import threading
import requests
import time

app = Flask(__name__)

# --- AIVEN CONFIGURATION ---
# Generate this at https://console.aiven.io/profile/auth
AIVEN_API_TOKEN = "wZnVDARBbkL8nUjdB7cc7qp55QZxGE1L7lt5VygDLPyXRYI/nPmSp2BDGFF8YnYAXEnjFlOpX1twHPka25k7Rz8a8DK6c6gKhAj9IUGKx+NN6wS7o2izbeKvLm+rZXAb0dpLBI4KXaXmXKtrZyafxj93QsQTV+97QkyalBYNvS2p1wvTIlLEwu1k9puKELU7SYK4HN7FLmjDg1AbgnMqJt/UAypP0U57x1uVt5gheJaQlbr8SfgSmSxOf7Ol5MeoLyj9Za7YAVcq5dT8BvjHoq8VZViD09QsUMIFrtYAKUQXZ7vDnhi6X+u7kLSqJrfV7S2HbzlrVPyibxY4+gXqUt4Gn+C9hAOr2tHTdHIB8wWg" 
AIVEN_PROJECT = "hacker-news-scraper" 
AIVEN_SERVICE = "hacker-news-scraper-mysql"

def ensure_db_is_on():
    """Checks Aiven service status. If POWEROFF, sends a start signal and waits."""
    url = f"https://api.aiven.io/v1/project/{AIVEN_PROJECT}/service/{AIVEN_SERVICE}"
    headers = {"Authorization": f"Bearer {AIVEN_API_TOKEN}"}
    
    try:
        response = requests.get(url, headers=headers)
        if response.status_code != 200:
            print(f"Aiven API Error: {response.status_code}")
            return
            
        service_data = response.json().get("service", {})
        state = service_data.get("state")
        
       
        if not service_data.get("powered") or state == "POWEROFF":
            print("Database is sleeping. Sending Power On command...")
            requests.put(url, headers=headers, json={"powered": True})
            
            
            while True:
                time.sleep(5)
                check = requests.get(url, headers=headers).json().get("service", {})
                current_state = check.get("state")
                print(f"Current DB State: {current_state}")
                if current_state == "RUNNING":
                    print("Database is ready!")
                    break
        else:
            print("Database is already awake and running.")
            
    except Exception as e:
        print(f"Failed to wake Aiven service: {e}")

def keep_alive():
    """Pings the Flask app and the Database to prevent BOTH from sleeping."""
    while True:
       
        try:
            requests.get("http://127.0.0.1:5000/health")
        except:
            pass
            
        
        try:
            db = mysql.connector.connect(
                host="hacker-news-scraper-mysql-hacker-news-scraper.i.aivencloud.com",
                port=26054,
                user="avnadmin",
                password="AVNS_O-JyMlJ__uSoVpa3Uas",
                database="scraper",
                ssl_ca="ca.pem" 
            )
            cursor = db.cursor()
            cursor.execute("SELECT 1")
            db.close()
            print("Database heartbeat successful.")
        except Exception as e:
            print(f"Heartbeat failed: {e}")

        time.sleep(600) # Run every 10 minutes

@app.route('/health')
def health():
    return "Alive", 200

def get_data_from_aiven():
    
    ensure_db_is_on()
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
   
    ensure_db_is_on()
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
