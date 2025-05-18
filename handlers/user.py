# handlers/admin.py

from aiogram import types

def register_handlers(dp):
    dp.message_handler(commands=["admin"])(admin_command)

async def admin_command(message: types.Message):
    await message.answer("Admin команда выполнена!")
