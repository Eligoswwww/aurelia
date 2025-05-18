async def get_access_token() -> str:
    auth_str = f"{PAYPAL_CLIENT_ID}:{PAYPAL_SECRET}"
    b64_auth = base64.b64encode(auth_str.encode()).decode()

    headers = {
        "Authorization": f"Basic {b64_auth}",
        "Content-Type": "application/x-www-form-urlencoded"
    }

    async with aiohttp.ClientSession() as session:
        async with session.post(
            f"{PAYPAL_API_BASE}/v1/oauth2/token",
            headers=headers,
            data="grant_type=client_credentials"
        ) as response:
            if response.status != 200:
                logger.error(f"Ошибка получения токена: {response.status}")
                raise Exception("Не удалось получить access token")
            data = await response.json()
            return data["access_token"]


async def create_paypal_order(amount: str = "5.00", currency: str = "USD") -> dict:
    token = await get_access_token()
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    body = {
        "intent": "CAPTURE",
        "purchase_units": [{
            "amount": {
                "currency_code": currency,
                "value": amount
            }
        }],
        "application_context": {
            "return_url": "https://example.com/return",  # заменишь на своё
            "cancel_url": "https://example.com/cancel"
        }
    }

    async with aiohttp.ClientSession() as session:
        async with session.post(f"{PAYPAL_API_BASE}/v2/checkout/orders", headers=headers, json=body) as response:
            if response.status != 201:
                logger.error(f"Ошибка создания заказа: {response.status}")
                raise Exception("Не удалось создать PayPal заказ")
            return await response.json()


async def capture_paypal_order(order_id: str) -> dict:
    token = await get_access_token()
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    async with aiohttp.ClientSession() as session:
        async with session.post(
            f"{PAYPAL_API_BASE}/v2/checkout/orders/{order_id}/capture",
            headers=headers
        ) as response:
            if response.status != 201:
                logger.error(f"Ошибка подтверждения оплаты: {response.status}")
                raise Exception("Не удалось подтвердить оплату")
            return await response.json()
