# handlers/user.py
from aiogram import types, Dispatcher
from aiogram.filters import Command, Text
from chatter.core import get_response, train_default, train_custom, reset_db

async def cmd_start(message: types.Message):
    await message.answer("👋 Привет! Я бот, обученный на ChatterBot. Напиши мне что-нибудь!")

async def cmd_help(message: types.Message):
    await message.answer("💬 Команды:\n/start — начать\n/help — помощь\n/train — обучить\n/reset — сбросить базу")

async def cmd_train(message: types.Message):
    train_default()
    await message.answer("🧠 Бот обучен стандартному русскому корпусу!")

async def cmd_reset(message: types.Message):
    if reset_db():
        await message.answer("🗑️ База сброшена. Выполни /train для переобучения.")
    else:
        await message.answer("⚠️ Не удалось сбросить базу.")

async def text_handler(message: types.Message):
    text = message.text.strip()
    if not text:
        return
    reply = get_response(text)
    await message.answer(reply)

async def read_chapter_1_handler(callback: types.CallbackQuery):
    await callback.message.answer("Текст Главы 1...")
    await callback.answer()

async def full_access_handler(callback: types.CallbackQuery):
    await callback.message.answer("Чтобы получить полный доступ, оформите подписку.")
    await callback.answer()

async def subscribe_handler(callback: types.CallbackQuery):
    await callback.message.answer("Чтобы подписаться, перейдите по ссылке или выберите способ оплаты.")
    await callback.answer()

async def read_full_book_handler(callback: types.CallbackQuery):
    await callback.message.answer("Вы получили полный доступ к книге! Вот весь текст...")
    await callback.answer()

def register_handlers(dp: Dispatcher):
    dp.message.register(cmd_start, Command(commands=["start"]))
    dp.message.register(cmd_help, Command(commands=["help"]))
    dp.message.register(cmd_train, Command(commands=["train"]))
    dp.message.register(cmd_reset, Command(commands=["reset"]))
    dp.message.register(text_handler)

def register_user_callbacks(dp: Dispatcher):
    dp.callback_query.register(read_chapter_1_handler, Text("read_chapter_1"))
    dp.callback_query.register(full_access_handler, Text("full_access"))
    dp.callback_query.register(subscribe_handler, Text("subscribe"))
    dp.callback_query.register(read_full_book_handler, Text("read_full_book"))
