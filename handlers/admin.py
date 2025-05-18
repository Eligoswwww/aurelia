import os
from aiogram import types, F
from aiogram.filters import Command
from db.session import async_session
from db.models import User
from payments.orders import create_order
from keyboards.admin import ADMIN_PANEL
from keyboards.user import USER_PANEL

ADMIN_ID = int(os.getenv("ADMIN_ID", "0"))

def register_handlers(dp):
    dp.message.register(cmd_start, Command("start"))
    dp.callback_query.register(admin_create_subscription, F.data == "admin_create_subscription")
    dp.callback_query.register(admin_create_chapter, F.data == "admin_create_chapter")
    dp.callback_query.register(admin_check_user, F.data == "admin_check_user")

async def cmd_start(message: types.Message):
    user_id = message.from_user.id
    text = "Привет! Выберите действие:"
    if user_id == ADMIN_ID:
        await message.answer("Админ-панель", reply_markup=ADMIN_PANEL)
        await message.answer(text, reply_markup=USER_PANEL)
    else:
        await message.answer(text, reply_markup=USER_PANEL)

async def admin_create_subscription(callback: types.CallbackQuery):
    await callback.answer()
    async with async_session() as session:
        order = await create_order(session, user_id=ADMIN_ID, order_type="subscription", amount=10.0)
    await callback.message.answer(f"Создан заказ подписки с ID {order.id}")

async def admin_create_chapter(callback: types.CallbackQuery):
    await callback.answer()
    part_id = 1
    async with async_session() as session:
        order = await create_order(session, user_id=ADMIN_ID, order_type="chapter", amount=2.0, part_id=part_id)
    await callback.message.answer(f"Создан заказ главы (ID части книги {part_id}) с ID заказа {order.id}")

async def admin_check_user(callback: types.CallbackQuery):
    await callback.answer()
    async with async_session() as session:
        result = await session.execute(select(User).where(User.telegram_id == ADMIN_ID))
        user = result.scalar_one_or_none()
    if user:
        status = "подписан" if user.subscribed else "не подписан"
        expire = user.subscription_expire.strftime("%Y-%m-%d %H:%M") if user.subscription_expire else "нет срока"
        await callback.message.answer(f"Пользователь {user.telegram_id}: {status}, действует до: {expire}")
    else:
        await callback.message.answer("Пользователь не найден.")
