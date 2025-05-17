import os
import logging
from aiogram import Bot, Dispatcher, types, F
from aiogram.types import BotCommand
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application
from aiohttp import web
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from datetime import datetime

from db.session import async_session
from db.models import User, UserPurchase, BookPart
from payments.orders import create_order, mark_order_paid
from keyboards.admin import ADMIN_PANEL
from keyboards.user import USER_PANEL

# --- Получение переменных окружения ---
TOKEN = os.getenv("BOT_TOKEN")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")
PORT = int(os.getenv("PORT", "10000"))
ADMIN_ID = int(os.getenv("ADMIN_ID", "0"))

if not TOKEN or not WEBHOOK_URL or not ADMIN_ID:
    raise ValueError("BOT_TOKEN, WEBHOOK_URL и ADMIN_ID должны быть заданы через переменные окружения")

# --- Настройка логгирования ---
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# --- Инициализация бота и диспетчера ---
bot = Bot(token=TOKEN)
dp = Dispatcher(storage=MemoryStorage())

# --- Обработка команды /start ---
from aiogram.filters import Command

@dp.message(Command("start"))

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
    async with async_session() as session:
        order = await create_order(session, user_id=ADMIN_ID, order_type="subscription", amount=10.0)
    await callback.message.answer(f"Создан заказ подписки с ID {order.id}")

@dp.callback_query(F.data == "admin_create_chapter")
async def admin_create_chapter(callback: types.CallbackQuery):
    await callback.answer()
    part_id = 1
    async with async_session() as session:
        order = await create_order(session, user_id=ADMIN_ID, order_type="chapter", amount=2.0, part_id=part_id)
    await callback.message.answer(f"Создан заказ главы (ID части книги {part_id}) с ID заказа {order.id}")

@dp.callback_query(F.data == "admin_check_user")
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

# --- Обработчики пользовательских кнопок ---
@dp.callback_query(F.data == "read_chapter_1")
async def user_read_chapter_1(callback: types.CallbackQuery):
    await callback.answer()
    await callback.message.answer("Вот текст Главы 1... (замени на реальный)")

@dp.callback_query(F.data == "full_access")
async def user_full_access(callback: types.CallbackQuery):
    await callback.answer()
    await callback.message.answer("Полный доступ пока не реализован. Скоро будет!")

@dp.callback_query(F.data == "open_store")
async def user_open_store(callback: types.CallbackQuery):
    await callback.answer()
    await callback.message.answer("Перейдите в наш магазин: https://example.com/store")

@dp.callback_query(F.data == "subscribe")
async def user_subscribe(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    await callback.answer()
    async with async_session() as session:
        order = await create_order(session, user_id=user_id, order_type="subscription", amount=10.0)
    await callback.message.answer(
        f"Для покупки подписки, пожалуйста, оплатите заказ №{order.id} на сумму {order.amount}$. (Оплата реализуется отдельно)"
    )

# --- Startup / Shutdown ---
async def on_startup(app: web.Application):
    await bot.set_webhook(WEBHOOK_URL)
    logger.info(f"Webhook установлен: {WEBHOOK_URL}")

async def on_shutdown(app: web.Application):
    logger.info("Выключение бота...")
    await bot.delete_webhook()
    await bot.session.close()

# --- Запуск приложения ---
app = web.Application()
app.on_startup.append(on_startup)
app.on_shutdown.append(on_shutdown)

SimpleRequestHandler(dispatcher=dp, bot=bot).register(app, path="/webhook")

if __name__ == "__main__":
    setup_application(app, dp, bot=bot)
    logger.info(f"Бот запущен на порту {PORT}")
    web.run_app(app, host="0.0.0.0", port=PORT)
