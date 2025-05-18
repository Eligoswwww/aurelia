import os
import logging
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application
from aiohttp import web
import handlers.admin as admin
import handlers.user as user
import handlers.paypal as paypal
import handlers.nemo as nemo

nemo.register_handlers(dp)

# --- Конфиг ---
TOKEN = os.getenv("BOT_TOKEN")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")
PORT = int(os.getenv("PORT", "10000"))
ADMIN_ID = int(os.getenv("ADMIN_ID", "0"))

if not TOKEN or not WEBHOOK_URL or not ADMIN_ID:
    raise ValueError("BOT_TOKEN, WEBHOOK_URL и ADMIN_ID должны быть заданы")

# --- Логгирование ---
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# --- Инициализация бота и диспетчера ---
bot = Bot(token=TOKEN)
dp = Dispatcher(storage=MemoryStorage())  # создаём диспетчер один раз

# --- Регистрация обработчиков ---
admin.register_handlers(dp)
user.register_handlers(dp)
paypal.register_handlers(dp)

# --- События старта и остановки ---
async def on_startup(app: web.Application):
    logger.info("⚡ on_startup вызван")
    await bot.set_webhook(WEBHOOK_URL)
    logger.info(f"Webhook установлен: {WEBHOOK_URL}")

async def on_shutdown(app: web.Application):
    logger.info("Выключение бота...")
    await bot.delete_webhook()
    await bot.session.close()

# --- Создаем веб-приложение aiohttp ---
app = web.Application()
app.on_startup.append(on_startup)
app.on_shutdown.append(on_shutdown)

# --- Роуты для PayPal ---
app.router.add_get("/paypal-success", paypal.paypal_success)
app.router.add_get("/paypal-cancel", paypal.paypal_cancel)

# --- Регистрируем webhook ---
SimpleRequestHandler(dispatcher=dp, bot=bot).register(app, path="/webhook")

if __name__ == "__main__":
    setup_application(app, dp, bot=bot)
    logger.info(f"Бот запущен на порту {PORT}")
    web.run_app(app, host="0.0.0.0", port=PORT)
