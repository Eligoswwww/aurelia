from aiogram import Dispatcher, types

ADMIN_IDS = [123456789]  # Замени на реальные ID

async def admin_command(message: types.Message):
    if message.from_user.id not in ADMIN_IDS:
        await message.reply("У вас нет доступа к этой команде.")
        return
    await message.answer("Admin команда выполнена!")

def register_handlers(dp: Dispatcher):
    dp.register_message_handler(admin_command, commands=["admin"])
