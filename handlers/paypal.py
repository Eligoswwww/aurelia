import logging
from aiohttp import web
from db.session import async_session
from payments.orders import mark_order_paid_by_paypal
from utils.payment_helpers import capture_paypal_order
from bot import bot  # Импорт бота для отправки сообщений

def register_handlers(dp):
    # Если нужно, сюда можно добавить регистрацию хендлеров, сейчас webhook идут через aiohttp
    pass

async def paypal_success(request: web.Request):
    user_id = int(request.query.get("user_id", 0))
    token = request.query.get("token")  # PayPal order id
    if not token or not user_id:
        return web.Response(text="Invalid parameters", status=400)

    success = await capture_paypal_order(token)
    if not success:
        return web.Response(text="Payment capture failed", status=400)

    async with async_session() as session:
        await mark_order_paid_by_paypal(session, token)

    try:
        await bot.send_message(user_id, "Оплата прошла успешно! Теперь у вас полный доступ к книге.")
    except Exception as e:
        logging.error(f"Ошибка при отправке сообщения: {e}")

    return web.Response(text="Payment successful. You can close this page.")

async def paypal_cancel(request: web.Request):
    return web.Response(text="Оплата была отменена пользователем.")
