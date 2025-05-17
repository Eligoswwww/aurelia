from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

ADMIN_PANEL = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="Создать заказ подписки", callback_data="admin_create_subscription"),
         InlineKeyboardButton(text="Создать заказ главы", callback_data="admin_create_chapter")],
        [InlineKeyboardButton(text="Проверить статус пользователя", callback_data="admin_check_user")]
    ]
)
