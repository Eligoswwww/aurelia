# пример заглушек, ты подставишь реальную логику
async def create_paypal_payment(session, user_id: int, amount: float, return_url: str, cancel_url: str):
    # здесь создаём платеж через API PayPal и возвращаем (order, approve_url)
    # заглушка:
    order = None
    approve_url = "https://paypal.com/approve-link"
    return order, approve_url

async def capture_paypal_order(token: str):
    # здесь реализуй захват платежа через PayPal API
    # заглушка:
    return True
