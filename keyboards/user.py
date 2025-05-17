from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

USER_PANEL = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="Читать Главу 1", callback_data="button_1")],
        [InlineKeyboardButton(text="Полный доступ", callback_data="button_2")],
        [InlineKeyboardButton(text="Посмотреть в магазине", callback_data="button_3")],
        [InlineKeyboardButton(text="Подписаться", callback_data="button_4")],
        
    ]
)
