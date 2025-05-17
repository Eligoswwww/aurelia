from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

def main_menu():
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add(KeyboardButton('/start'))
    keyboard.add(KeyboardButton('Чтение'))
    keyboard.add(KeyboardButton('Помощь'))
    return keyboard
