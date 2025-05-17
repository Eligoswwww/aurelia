from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

USER_PANEL = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="Читать Главу 1", callback_data="read_chapter_1")],
        [InlineKeyboardButton(text="Полный доступ", callback_data="full_access")],
        [InlineKeyboardButton(text="Посмотреть в магазине", callback_data="open_store")],
        [InlineKeyboardButton(text="Подписаться", callback_data="subscribe")],
    ]
)
