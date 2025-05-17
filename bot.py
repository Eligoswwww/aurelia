import os
import logging
import aiohttp  # Добавлено для загрузки текста с Google Drive

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
from payments.orders import create_order, mark_order_paid, pay_and_unlock_full_book
from keyboards.admin import ADMIN_PANEL
from keyboards.user import USER_PANEL, FULL_ACCESS_PANEL

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

# --- Импорт фильтра команд ---
from aiogram.filters import Command

# --- Обработка команды /start ---
@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    user_id = message.from_user.id
    text = "Привет! Выберите действие:"
    if user_id == ADMIN_ID:
        await message.answer("Админ-панель", reply_markup=ADMIN_PANEL)
        await message.answer(text, reply_markup=USER_PANEL)
    else:
        await message.answer(text, reply_markup=USER_PANEL)

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

@dp.callback_query(F.data == "full_access")
async def user_full_access(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    await callback.answer("Создаём заказ...")

    async with async_session() as session:
        # Создание заказа
        order = await create_order(
            session,
            user_id=user_id,
            order_type="full_access",
            amount=15.0,
        )
        # Платим (заглушка)
        success = await pay_and_unlock_full_book(session, user_id, order)

    if success:
        await callback.message.answer(
            "✅ Полный доступ получен! Теперь вы можете читать всю книгу.",
            reply_markup=FULL_ACCESS_PANEL
        )
    else:
        await callback.message.answer("❌ Не удалось оплатить. Попробуйте позже.")

@dp.callback_query(F.data == "read_full_book")
async def user_read_full_book(callback: types.CallbackQuery):
    await callback.answer()
    await callback.message.answer("📖 Вот текст всей книги... (вставь сюда реальный текст или загрузку)")

# --- Обработчики пользовательских кнопок ---

@dp.callback_query(F.data == "read_chapter_1")
async def user_read_chapter_1(callback: types.CallbackQuery):
    await callback.answer()

    GOOGLE_FILE_ID = "13bEJM5s6kmexUHW_MCMfbm1TnXRIrLip"
    file_url = f"https://drive.google.com/uc?export=download&id={GOOGLE_FILE_ID}"

    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(file_url) as resp:
                if resp.status == 200:
                    text = await resp.text()

                    # Отправка текста частями, если превышает лимит
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
    print("⚡ on_startup вызван")  # Эта строка проверит, вызывается ли startup
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
