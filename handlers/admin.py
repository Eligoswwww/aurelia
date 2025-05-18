from aiogram import Dispatcher, types

ADMIN_IDS = [7617589302]  # Замени на реальные ID

async def admin_command(message: types.Message):
    if message.from_user.id not in ADMIN_IDS:
        await message.reply("У вас нет доступа к этой команде.")
        return
    await message.answer("Admin команда выполнена!")

def register_handlers(dp: Dispatcher):
    # Здесь исправлено с register_message_handler на dp.message.register
    dp.message.register(admin_command, commands=["admin"])
