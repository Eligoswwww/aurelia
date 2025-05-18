import os
import threading
import time
import requests
from flask import Flask, request

app = Flask(__name__)

@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.get_json()
    print(data)
    return '', 200

@app.route('/health', methods=['GET'])
def health():
    return 'OK', 200

def ping_self():
    port = int(os.environ.get('PORT', 5000))
    url = f"http://localhost:{port}/health"
    while True:
        try:
            requests.get(url)
        except:
            pass
        time.sleep(600)  # 10 минут

if __name__ == '__main__':
    threading.Thread(target=ping_self, daemon=True).start()
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
