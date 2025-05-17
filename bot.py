import os
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.types import BotCommand
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application
from aiohttp import web
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

TOKEN = os.getenv("BOT_TOKEN")
WEBHOOK_PATH = f"/webhook"
WEBHOOK_URL = os.getenv("WEBHOOK_URL") + WEBHOOK_PATH
PORT = int(os.getenv("PORT", default=8080))

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Bot and Dispatcher setup
bot = Bot(token=TOKEN)
dp = Dispatcher(storage=MemoryStorage())

# Sample command handler
@dp.message(commands=["start"])
async def cmd_start(message: types.Message):
    await message.answer("Привет! Я бот проекта AURELIA.")

# Main webhook setup
async def on_startup(app: web.Application):
    await bot.set_webhook(WEBHOOK_URL)
    logger.info(f"Webhook set to {WEBHOOK_URL}")

async def on_shutdown(app: web.Application):
    logger.info("Shutting down...")
    await bot.delete_webhook()
    await bot.session.close()

# Aiohttp application setup
app = web.Application()
app.on_startup.append(on_startup)
app.on_shutdown.append(on_shutdown)

SimpleRequestHandler(dispatcher=dp, bot=bot).register(app, path=WEBHOOK_PATH)

if __name__ == '__main__':
    setup_application(app, dp, bot=bot)
    web.run_app(app, host="0.0.0.0", port=PORT)
