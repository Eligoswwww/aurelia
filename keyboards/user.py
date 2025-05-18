# handlers/user.py
from aiogram import types, Dispatcher
from aiogram.filters import Text

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

def register_user_callbacks(dp: Dispatcher):
    dp.callback_query.register(read_chapter_1_handler, Text("read_chapter_1"))
    dp.callback_query.register(full_access_handler, Text("full_access"))
    dp.callback_query.register(subscribe_handler, Text("subscribe"))
    dp.callback_query.register(read_full_book_handler, Text("read_full_book"))
