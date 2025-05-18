from aiogram import types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

# Кнопки админ-панели
ADMIN_PANEL = InlineKeyboardMarkup(inline_keyboard=[
    [
        InlineKeyboardButton(text="Создать заказ подписки", callback_data="admin_create_subscription"),
        InlineKeyboardButton(text="Создать заказ главы", callback_data="admin_create_chapter")
    ],
    [InlineKeyboardButton(text="Проверить статус пользователя", callback_data="admin_check_user")]
])

# Кнопки пользователя для тестов в админ-панели
USER_TEST_PANEL = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="Читать Главу 1", callback_data="read_chapter_1")],
    [InlineKeyboardButton(text="Полный доступ", callback_data="full_access")],
    [InlineKeyboardButton(text="Подписаться", callback_data="subscribe")],
    [InlineKeyboardButton(text="Читать всю книгу", callback_data="read_full_book")],
])

# Главная панель админа
ADMIN_MAIN_PANEL = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="Админ функции", callback_data="show_admin_panel")],
    [InlineKeyboardButton(text="Тестовые кнопки пользователя", callback_data="show_user_panel")]
])

async def admin_start_handler(callback: types.CallbackQuery):
    await callback.message.answer("Вы в админ-меню", reply_markup=ADMIN_MAIN_PANEL)
    await callback.answer()

async def show_admin_panel_handler(callback: types.CallbackQuery):
    await callback.message.edit_text("Админ-панель:", reply_markup=ADMIN_PANEL)
    await callback.answer()

async def show_user_panel_handler(callback: types.CallbackQuery):
    await callback.message.edit_text("Панель пользователя (тест):", reply_markup=USER_TEST_PANEL)
    await callback.answer()

# Обработчики админ-панели
async def admin_create_subscription_handler(callback: types.CallbackQuery):
    await callback.message.answer("Создание заказа подписки — в разработке.")
    await callback.answer()

async def admin_create_chapter_handler(callback: types.CallbackQuery):
    await callback.message.answer("Создание заказа главы — в разработке.")
    await callback.answer()

async def admin_check_user_handler(callback: types.CallbackQuery):
    await callback.message.answer("Проверка статуса пользователя — в разработке.")
    await callback.answer()

# Обработчики тестовых кнопок пользователя
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

def register_handlers(dp):
    # Регистрация callback_query обработчиков с фильтрами по callback_data
    dp.callback_query.register(admin_start_handler, lambda c: c.data == "admin_start")
    dp.callback_query.register(show_admin_panel_handler, lambda c: c.data == "show_admin_panel")
    dp.callback_query.register(show_user_panel_handler, lambda c: c.data == "show_user_panel")

    dp.callback_query.register(admin_create_subscription_handler, lambda c: c.data == "admin_create_subscription")
    dp.callback_query.register(admin_create_chapter_handler, lambda c: c.data == "admin_create_chapter")
    dp.callback_query.register(admin_check_user_handler, lambda c: c.data == "admin_check_user")

    dp.callback_query.register(read_chapter_1_handler, lambda c: c.data == "read_chapter_1")
    dp.callback_query.register(full_access_handler, lambda c: c.data == "full_access")
    dp.callback_query.register(subscribe_handler, lambda c: c.data == "subscribe")
    dp.callback_query.register(read_full_book_handler, lambda c: c.data == "read_full_book")
