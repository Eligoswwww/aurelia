import os
import logging
from aiogram import Bot, Dispatcher, types, F
from aiogram.types import BotCommand
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application
from aiohttp import web
from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from datetime import datetime

from db.session import async_session
from db.models import User, UserPurchase, BookPart
from payments.orders import create_order, mark_order_paid
from keyboards.admin import ADMIN_PANEL
from keyboards.user import USER_PANEL

load_dotenv()

TOKEN = os.getenv("BOT_TOKEN")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")
PORT = int(os.getenv("PORT", "10000"))
ADMIN_ID = int(os.getenv("ADMIN_ID", "0"))

if not TOKEN or not WEBHOOK_URL or not ADMIN_ID:
    raise ValueError("BOT_TOKEN, WEBHOOK_URL и ADMIN_ID должны быть заданы")

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

bot = Bot(token=TOKEN)
dp = Dispatcher(storage=MemoryStorage())

# --- Хэндлер команды /start ---
@dp.message(F.text == "/start")
async def cmd_start(message: types.Message):
    user_id = message.from_user.id
    if user_id == ADMIN_ID:
        await message.answer("Админ-панель", reply_markup=ADMIN_PANEL)
    else:
        await message.answer("Привет! Выберите действие:", reply_markup=USER_PANEL)

# --- Обработчики админских кнопок ---
@dp.callback_query(F.data == "admin_create_subscription")
async def admin_create_subscription(callback: types.CallbackQuery):
    await callback.answer()
    # Пример: создаем заказ подписки за 10$
    async with async_session() as session:
        order = await create_order(session, user_id=ADMIN_ID, order_type="subscription", amount=10.0)
    await callback.message.answer(f"Создан заказ подписки с ID {order.id}")

@dp.callback_query(F.data == "admin_create_chapter")
async def admin_create_chapter(callback: types.CallbackQuery):
    await callback.answer()
    # Пример: выбираем часть книги с id=1 (замени по необходимости)
    part_id = 1
    async with async_session() as session:
        order = await create_order(session, user_id=ADMIN_ID, order_type="chapter", amount=2.0, part_id=part_id)
    await callback.message.answer(f"Создан заказ главы (ID части книги {part_id}) с ID заказа {order.id}")

@dp.callback_query(F.data == "admin_check_user")
async def admin_check_user(callback: types.CallbackQuery):
    await callback.answer()
    # Просто пример - проверим подписку на ADMIN_ID
    async with async_session() as session:
        result = await session.execute(select(User).where(User.telegram_id == ADMIN_ID))
        user = result.scalar_one_or_none()
    if user:
        status = "подписан" if user.subscribed else "не подписан"
        expire = user.subscription_expire.strftime("%Y-%m-%d %H:%M") if user.subscription_expire else "нет срока"
        await callback.message.answer(f"Пользователь {user.telegram_id}: {status}, действует до: {expire}")
    else:
        await callback.message.answer("Пользователь не найден.")

# --- Обработчики пользовательских кнопок ---
@dp.callback_query(F.data == "user_my_access")
async def user_my_access(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    async with async_session() as session:
        result = await session.execute(select(User).where(User.telegram_id == user_id))
        user = result.scalar_one_or_none()
        if not user:
            await callback.message.answer("Вы не зарегистрированы в системе.")
            return
        
        text = f"Подписка: {'активна' if user.subscribed else 'отсутствует'}\n"
        if user.subscription_expire:
            text += f"Действует до: {user.subscription_expire.strftime('%Y-%m-%d %H:%M')}\n"
        
        # Покупки пользователя
        purchases = await session.execute(
            select(UserPurchase).where(UserPurchase.user_id == user.id)
        )
        parts = purchases.scalars().all()
        if parts:
            text += "Купленные главы:\n"
            for p in parts:
                text += f"- {p.part.title}\n"
        else:
            text += "Нет купленных глав."
        
        await callback.message.answer(text)

@dp.callback_query(F.data == "user_buy_subscription")
async def user_buy_subscription(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    async with async_session() as session:
        # Создаем заказ подписки (цена примерная)
        order = await create_order(session, user_id=user_id, order_type="subscription", amount=10.0)
    await callback.message.answer(f"Для покупки подписки, пожалуйста, оплатите заказ №{order.id} на сумму {order.amount}$. (Оплата реализуется отдельно)")

# --- Startup / Shutdown ---
async def on_startup(app: web.Application):
    await bot.set_webhook(WEBHOOK_URL)
    logger.info(f"Webhook установлен: {WEBHOOK_URL}")

async def on_shutdown(app: web.Application):
    logger.info("Выключение бота...")
    await bot.delete_webhook()
    await bot.session.close()

app = web.Application()
app.on_startup.append(on_startup)
app.on_shutdown.append(on_shutdown)

SimpleRequestHandler(dispatcher=dp, bot=bot).register(app, path="/webhook")

if __name__ == "__main__":
    setup_application(app, dp, bot=bot)
    web.run_app(app, host="0.0.0.0", port=PORT)
