from aiogram import types
from aiohttp import web
import logging

from utils.paypal_api import create_paypal_order, capture_paypal_order  # твой модуль с функциями

logger = logging.getLogger(__name__)

def register_handlers(dp):
    dp.message_handler(commands=["pay"])(pay_command)

async def pay_command(message: types.Message):
    amount = 5.0  # Сумма для примера
    # Ссылки на редиректы после оплаты
    return_url = "https://yourdomain.com/paypal-success"
    cancel_url = "https://yourdomain.com/paypal-cancel"

    order_id, approve_url = await create_paypal_order(amount, return_url, cancel_url)
    if approve_url:
        await message.answer(f"Пожалуйста, оплатите по ссылке: {approve_url}")
    else:
        await message.answer("Не удалось создать заказ PayPal, попробуйте позже.")

# aiohttp handlers для PayPal webhook или редиректов

async def paypal_success(request: web.Request):
    # здесь обычно берется order_id из параметров запроса
    order_id = request.query.get("token")
    if not order_id:
        return web.Response(text="Order ID не указан", status=400)

    success, capture_id = await capture_paypal_order(order_id)
    if success:
        logger.info(f"Оплата подтверждена, capture_id: {capture_id}")
        return web.Response(text="Оплата успешно завершена. Спасибо!")
    else:
        logger.warning("Оплата не подтверждена или не завершена")
        return web.Response(text="Оплата не подтверждена. Попробуйте еще раз.")

async def paypal_cancel(request: web.Request):
    return web.Response(text="Оплата отменена пользователем.")
