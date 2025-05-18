from aiogram import Dispatcher, types
from aiogram.filters import Command

async def admin_command(message: types.Message):
    # твой код для обработки команды /admin
    await message.answer("Admin panel accessed")

def register_handlers(dp: Dispatcher):
    dp.message.register(admin_command, Command(commands=["admin"]))
