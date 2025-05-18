import os
import aiohttp
import base64
import logging

PAYPAL_CLIENT_ID = os.getenv("PAYPAL_CLIENT_ID")
PAYPAL_SECRET = os.getenv("PAYPAL_SECRET")
PAYPAL_API_BASE = "https://api-m.sandbox.paypal.com"  # для sandbox, для продакшена — https://api-m.paypal.com

logger = logging.getLogger(__name__)

async def get_access_token():
    auth = base64.b64encode(f"{PAYPAL_CLIENT_ID}:{PAYPAL_SECRET}".encode()).decode()
    headers = {
        "Authorization": f"Basic {auth}",
        "Content-Type": "application/x-www-form-urlencoded"
    }
    data = "grant_type=client_credentials"
    async with aiohttp.ClientSession() as session:
        async with session.post(f"{PAYPAL_API_BASE}/v1/oauth2/token", headers=headers, data=data) as resp:
            res = await resp.json()
            if resp.status != 200:
                logger.error(f"PayPal get_access_token error: {res}")
                return None
            return res["access_token"]

async def create_paypal_order(amount: float, return_url: str, cancel_url: str):
    token = await get_access_token()
    if not token:
        return None

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    order_payload = {
        "intent": "CAPTURE",
        "purchase_units": [{
            "amount": {
                "currency_code": "USD",
                "value": f"{amount:.2f}"
            }
        }],
        "application_context": {
            "return_url": return_url,
            "cancel_url": cancel_url
        }
    }

    async with aiohttp.ClientSession() as session:
        async with session.post(f"{PAYPAL_API_BASE}/v2/checkout/orders", json=order_payload, headers=headers) as resp:
            res = await resp.json()
            if resp.status != 201:
                logger.error(f"PayPal create order error: {res}")
                return None
            # Ищем ссылку на approve (куда отправить пользователя)
            for link in res.get("links", []):
                if link["rel"] == "approve":
                    return res["id"], link["href"]
            return res["id"], None

async def capture_paypal_order(order_id: str):
    token = await get_access_token()
    if not token:
        return False
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    async with aiohttp.ClientSession() as session:
        async with session.post(f"{PAYPAL_API_BASE}/v2/checkout/orders/{order_id}/capture", headers=headers) as resp:
            res = await resp.json()
            if resp.status != 201:
                logger.error(f"PayPal capture order error: {res}")
                return False
            # Можно проверить статус и т.п.
            return True
