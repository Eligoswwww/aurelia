from aiogram import types
from aiogram.filters import Command
import logging

logger = logging.getLogger(__name__)

async def admin_command(message: types.Message):
    logger.info("admin_command вызван")
    await message.answer("Admin команда выполнена!")

def register_handlers(dp):
    dp.message.register(admin_command, Command(commands=["admin"]))
