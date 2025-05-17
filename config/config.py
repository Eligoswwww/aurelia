import os
from dotenv import load_dotenv
load_dotenv()

TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
AES_KEY = os.getenv('AES_KEY', 'YourAESKeyHere123')  # Replace with secure key
