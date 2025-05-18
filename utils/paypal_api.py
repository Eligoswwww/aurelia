# utils/paypal_api.py
import os
import aiohttp
import base64
import logging

PAYPAL_CLIENT_ID = os.getenv("PAYPAL_CLIENT_ID")
PAYPAL_SECRET = os.getenv("PAYPAL_SECRET")
PAYPAL_API_BASE = "https://api-m.sandbox.paypal.com"

logger = logging.getLogger(__name__)

# ... (весь твой код функций get_access_token, create_paypal_order, capture_paypal_order)
