from aiogram import types, Dispatcher
from aiogram.filters import Command

async def cmd_start(message: types.Message):
    await message.answer("Привет! Бот работает и отвечает на команду /start.")

def register_handlers(dp: Dispatcher):
    dp.message.register(cmd_start, Command(commands=["start"]))
