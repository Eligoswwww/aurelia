# payments/mock_gateway.py

async def process_payment(order_id: int, amount: float) -> bool:
    # Здесь будет интеграция с реальной платёжной системой
    # Сейчас это просто успешная заглушка
    print(f"🔄 Имитируем оплату: заказ #{order_id}, сумма {amount}")
    return True
