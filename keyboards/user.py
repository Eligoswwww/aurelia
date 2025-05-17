from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

USER_PANEL = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="Кнопка 1", callback_data="button_1")],
        [InlineKeyboardButton(text="Кнопка 2", callback_data="button_2")],
    ]
)
