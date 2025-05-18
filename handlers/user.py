from aiogram import types
from aiogram.filters import Command  # импорт фильтра команд

async def admin_command(message: types.Message):
    await message.answer("Admin команда выполнена!")

def register_handlers(dp):
    dp.message.register(admin_command, Command(commands=["admin"]))
