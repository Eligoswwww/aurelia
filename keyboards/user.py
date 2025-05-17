from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

USER_PANEL = InlineKeyboardMarkup(row_width=1)
USER_PANEL.add(
    InlineKeyboardButton(text="Мои подписки и покупки", callback_data="user_my_access"),
    InlineKeyboardButton(text="Купить подписку", callback_data="user_buy_subscription"),
)
