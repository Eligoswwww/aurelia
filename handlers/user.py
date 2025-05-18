from aiogram import types

async def admin_command(message: types.Message):
    await message.answer("Admin команда выполнена!")

def register_handlers(dp):
    dp.message.register(admin_command, commands=["admin"])
