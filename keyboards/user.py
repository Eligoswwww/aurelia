from aiogram import types

async def read_chapter_1_handler(callback: types.CallbackQuery):
    # Здесь логика выдачи главы 1, например, проверка подписки и отправка текста
    await callback.message.answer("Текст Главы 1...")
    await callback.answer()

async def full_access_handler(callback: types.CallbackQuery):
    # Логика предоставления полного доступа, например, предложение купить подписку
    await callback.message.answer("Чтобы получить полный доступ, оформите подписку.")
    await callback.answer()

async def subscribe_handler(callback: types.CallbackQuery):
    # Запуск процесса подписки (например, вывод инструкции или ссылка)
    await callback.message.answer("Чтобы подписаться, перейдите по ссылке или выберите способ оплаты.")
    await callback.answer()

async def read_full_book_handler(callback: types.CallbackQuery):
    # Проверка прав доступа и выдача полной книги
    await callback.message.answer("Вы получили полный доступ к книге! Вот весь текст...")
    await callback.answer()

def register_user_callbacks(dp):
    dp.callback_query.register(read_chapter_1_handler, lambda c: c.data == "read_chapter_1")
    dp.callback_query.register(full_access_handler, lambda c: c.data == "full_access")
    dp.callback_query.register(subscribe_handler, lambda c: c.data == "subscribe")
    dp.callback_query.register(read_full_book_handler, lambda c: c.data == "read_full_book")
