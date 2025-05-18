import os
import logging
import aiohttp

from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application
from aiohttp import web
from sqlalchemy.future import select

from db.session import async_session
from db.models import User
from payments.orders import create_order, create_paypal_payment, mark_order_paid_by_paypal
from keyboards.admin import ADMIN_PANEL
from keyboards.user import USER_PANEL, FULL_ACCESS_PANEL

# --- Переменные окружения ---
TOKEN = os.getenv("BOT_TOKEN")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")
PORT = int(os.getenv("PORT", "10000"))
ADMIN_ID = int(os.getenv("ADMIN_ID", "0"))
WEBHOOK_DOMAIN = os.getenv("WEBHOOK_DOMAIN")  # Например: https://your-domain.com

if not TOKEN or not WEBHOOK_URL or not ADMIN_ID or not WEBHOOK_DOMAIN:
    raise ValueError("BOT_TOKEN, WEBHOOK_URL, ADMIN_ID и WEBHOOK_DOMAIN должны быть заданы через переменные окружения")

# --- Логгирование ---
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# --- Инициализация ---
bot = Bot(token=TOKEN)
dp = Dispatcher(storage=MemoryStorage())

# --- Обработка /start ---
@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    user_id = message.from_user.id
    text = "Привет! Выберите действие:"
    if user_id == ADMIN_ID:
        await message.answer("Админ-панель", reply_markup=ADMIN_PANEL)
        await message.answer(text, reply_markup=USER_PANEL)
    else:
        await message.answer(text, reply_markup=USER_PANEL)

# --- Обработчик кнопки "Полный доступ" ---
@dp.callback_query(F.data == "full_access")
async def full_access(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    await callback.answer("Создаём заказ...")

    async with async_session() as session:
        # Генерация URL для успешной и отменённой оплаты
        return_url = f"{WEBHOOK_DOMAIN}/paypal-success?user_id={user_id}"
        cancel_url = f"{WEBHOOK_DOMAIN}/paypal-cancel"

        # Создаём платеж через PayPal
        order, approve_url = await create_paypal_payment(session, user_id, 15.0, return_url, cancel_url)
        if approve_url:
            await callback.message.answer(
                f"Для оплаты перейдите по ссылке:\n{approve_url}\n\nПосле оплаты вы получите полный доступ к книге."
            )
        else:
            await callback.message.answer("Ошибка создания платежа, попробуйте позже.")

# --- Обработчик успешной оплаты PayPal ---
async def paypal_success(request: web.Request):
    user_id = request.query.get("user_id")
    token = request.query.get("token")  # PayPal order id

    if not user_id or not token:
        return web.Response(text="Invalid parameters", status=400)

    try:
        user_id = int(user_id)
    except ValueError:
        return web.Response(text="Invalid user_id", status=400)

    # Завершаем оплату через PayPal API
    success = await mark_order_paid_by_paypal(token)
    if not success:
        return web.Response(text="Payment capture failed", status=400)

    # Отправляем пользователю сообщение об успешной оплате
    try:
        await bot.send_message(user_id, "Оплата прошла успешно! Теперь у вас полный доступ к книге.")
    except Exception as e:
        logger.error(f"Ошибка при отправке сообщения: {e}")

    return web.Response(text="Оплата успешна. Вы можете закрыть эту страницу.")

# --- Обработчик отмены оплаты ---
async def paypal_cancel(request: web.Request):
    return web.Response(text="Оплата была отменена пользователем.")

# --- Пример обработки чтения главы (для полноты) ---
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
                    if len(text) <= 4096:
                        await callback.message.answer(text)
                    else:
                        parts = [text[i:i+4096] for i in range(0, len(text), 4096)]
                        for part in parts:
                            await callback.message.answer(part)
                else:
                    await callback.message.answer("Не удалось загрузить главу. Попробуйте позже.")
    except Exception as e:
        logger.error(f"Ошибка при загрузке главы: {e}")
        await callback.message.answer("Произошла ошибка при загрузке текста.")

# --- Запуск веб-приложения и вебхука ---
async def on_startup(app: web.Application):
    logger.info("Запуск бота, установка webhook...")
    await bot.set_webhook(WEBHOOK_URL)
    logger.info(f"Webhook установлен: {WEBHOOK_URL}")

async def on_shutdown(app: web.Application):
    logger.info("Выключение бота...")
    await bot.delete_webhook()
    await bot.session.close()

app = web.Application()
app.on_startup.append(on_startup)
app.on_shutdown.append(on_shutdown)

# Роуты для PayPal
app.router.add_get("/paypal-success", paypal_success)
app.router.add_get("/paypal-cancel", paypal_cancel)

# Регистрируем webhook
SimpleRequestHandler(dispatcher=dp, bot=bot).register(app, path="/webhook")

if __name__ == "__main__":
    setup_application(app, dp, bot=bot)
    logger.info(f"Бот запущен на порту {PORT}")
    web.run_app(app, host="0.0.0.0", port=PORT)
