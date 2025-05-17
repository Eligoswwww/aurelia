from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

USER_PANEL = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="Читать Главу 1", callback_data="read_chapter_1")],
        [InlineKeyboardButton(text="Полный доступ", callback_data="full_access")],
        [InlineKeyboardButton(text="Посмотреть в магазине", url="https://a.co/d/0lsFYNT")],
        [InlineKeyboardButton(text="Подписаться", callback_data="subscribe")],
    ]  # <-- закрываем список inline_keyboard
)  # <-- закрываем InlineKeyboardMarkup

FULL_ACCESS_PANEL = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="Читать всю книгу", callback_data="read_full_book")],
    ]
)
