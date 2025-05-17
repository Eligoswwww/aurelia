import os
import logging
from aiogram import Bot, Dispatcher, types, F
from aiogram.types import BotCommand
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application
from aiohttp import web
from dotenv import load_dotenv

# 🔐 Загружаем переменные окружения из .env
load_dotenv()

# 📦 Получаем конфигурацию
TOKEN = os.getenv("BOT_TOKEN")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")
PORT = int(os.getenv("PORT", "10000"))

# 🚫 Обязательные переменные
if not TOKEN or not WEBHOOK_URL:
    raise ValueError("BOT_TOKEN и WEBHOOK_URL должны быть в .env")

# 📋 Настраиваем логирование
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 🤖 Инициализируем бота и диспетчер
bot = Bot(token=TOKEN)
dp = Dispatcher(storage=MemoryStorage())

# ✅ Обработчик команды /start с фильтром aiogram 3.x
@dp.message(F.text == "/start")
async def cmd_start(message: types.Message):
    await message.answer("Привет! Я протокол AURELIA.")

# 🚀 При старте приложения — устанавливаем webhook
async def on_startup(app: web.Application):
    await bot.set_webhook(WEBHOOK_URL)
    logger.info(f"Webhook установлен: {WEBHOOK_URL}")

# 📴 При выключении — удаляем webhook и закрываем сессию
async def on_shutdown(app: web.Application):
    logger.info("Выключение бота...")
    await bot.delete_webhook()
    await bot.session.close()

# 🌐 Инициализируем aiohttp-приложение и вешаем события
app = web.Application()
app.on_startup.append(on_startup)
app.on_shutdown.append(on_shutdown)

# 🌍 Обрабатываем входящие webhook-запросы на /webhook
SimpleRequestHandler(dispatcher=dp, bot=bot).register(app, path="/webhook")

# ▶️ Запускаем aiohttp-приложение
if __name__ == "__main__":
    setup_application(app, dp, bot=bot)
    web.run_app(app, host="0.0.0.0", port=PORT)
