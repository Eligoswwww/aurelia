import os
import logging
import aiohttp
from aiogram import types, F
from db.session import async_session
from payments.orders import create_order
from keyboards.user import USER_PANEL, FULL_ACCESS_PANEL
from utils.payment_helpers import create_paypal_order  # исправлено на create_paypal_order

def register_handlers(dp):
    dp.callback_query.register(full_access, F.data == "full_access")
    dp.callback_query.register(user_read_chapter_1, F.data == "read_chapter_1")
    dp.callback_query.register(user_open_store, F.data == "open_store")
    dp.callback_query.register(user_subscribe, F.data == "subscribe")

async def full_access(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    await callback.answer("Создаём заказ...")

    async with async_session() as session:
        domain = os.getenv("WEBHOOK_DOMAIN") or "https://your-domain.com"
        return_url = f"{domain}/paypal-success?user_id={user_id}"
        cancel_url = f"{domain}/paypal-cancel"

        order_id, approve_url = await create_paypal_order(15.0, return_url, cancel_url)
        if approve_url:
            await callback.message.answer(
                f"Для оплаты перейдите по ссылке:\n{approve_url}\n\nПосле оплаты вы получите доступ к книге."
            )
        else:
            await callback.message.answer("Ошибка создания платежа, попробуйте позже.")

async def user_read_chapter_1(callback: types.CallbackQuery):
    await callback.answer()

    GOOGLE_FILE_ID = "13bEJM5s6kmexUHW_MCMfbm1TnXRIrLip"
    file_url = f"https://drive.google.com/uc?export=download&id={GOOGLE_FILE_ID}"

    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(file_url) as resp:
                if resp.status == 200:
                    text = await resp.text()

                    if len(text) <= 4096:
                        await callback.message.answer(text)
                    else:
                        parts = [text[i:i+4096] for i in range(0, len(text), 4096)]
                        for part in parts:
                            await callback.message.answer(part)
                else:
                    await callback.message.answer("Не удалось загрузить главу. Попробуйте позже.")
    except Exception as e:
        logging.error(f"Ошибка при загрузке главы: {e}")
        await callback.message.answer("Произошла ошибка при загрузке текста.")

async def user_open_store(callback: types.CallbackQuery):
    await callback.answer()
    await callback.message.answer("Перейдите в наш магазин: https://example.com/store")

async def user_subscribe(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    await callback.answer()
    async with async_session() as session:
        order = await create_order(session, user_id=user_id, order_type="subscription", amount=10.0)
    await callback.message.answer(
        f"Для покупки подписки, пожалуйста, оплатите заказ №{order.id} на сумму {order.amount}$. (Оплата реализуется отдельно)"
    )
