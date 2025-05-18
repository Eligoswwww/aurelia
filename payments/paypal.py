import os
import aiohttp
import base64
import logging

PAYPAL_CLIENT_ID = os.getenv("PAYPAL_CLIENT_ID")
PAYPAL_SECRET = os.getenv("PAYPAL_SECRET")
# Для продакшена поменяй на: https://api-m.paypal.com
PAYPAL_API_BASE = "https://api-m.sandbox.paypal.com"

logger = logging.getLogger(__name__)

async def get_access_token() -> str | None:
    """
    Получение OAuth2 токена для авторизации запросов к PayPal API.
    """
    if not PAYPAL_CLIENT_ID or not PAYPAL_SECRET:
        logger.error("PayPal credentials are not set in environment variables")
        return None

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
            return res.get("access_token")

async def create_paypal_order(amount: float, return_url: str, cancel_url: str) -> tuple[str | None, str | None]:
    """
    Создаёт заказ PayPal и возвращает (paypal_order_id, approve_url).
    approve_url — это ссылка, на которую нужно отправить пользователя для оплаты.
    """
    token = await get_access_token()
    if not token:
        return None, None

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
                return None, None

            for link in res.get("links", []):
                if link.get("rel") == "approve":
                    return res.get("id"), link.get("href")
            # Если ссылка approve не найдена
            return res.get("id"), None

async def capture_paypal_order(order_id: str) -> tuple[bool, str | None]:
    """
    Подтверждает (захватывает) оплату по order_id.
    Возвращает (успех, capture_id) — capture_id пригодится для логов и сохранения.
    """
    token = await get_access_token()
    if not token:
        return False, None

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    async with aiohttp.ClientSession() as session:
        async with session.post(f"{PAYPAL_API_BASE}/v2/checkout/orders/{order_id}/capture", headers=headers) as resp:
            res = await resp.json()
            if resp.status != 201:
                logger.error(f"PayPal capture order error: {res}")
                return False, None

            # Проверяем статус capture
            captures = res.get("purchase_units", [])[0].get("payments", {}).get("captures", [])
            if not captures:
                logger.error(f"PayPal capture response has no captures: {res}")
                return False, None

            capture = captures[0]
            status = capture.get("status")
            capture_id = capture.get("id")

            if status == "COMPLETED":
                return True, capture_id
            else:
                logger.warning(f"PayPal capture not completed, status: {status}")
                return False, capture_id
