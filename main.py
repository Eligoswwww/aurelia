import logging
import sqlite3
from aiogram import Bot, Dispatcher, types
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.contrib.middlewares.logging import LoggingMiddleware
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.dispatcher import FSMContext
from aiogram.contrib.fsm_storage.memory import MemoryStorage
import asyncio

API_TOKEN = '7856167694:AAGBvMeEIBHFPeCpd6cob05vxaLIUDhay-0'  # <-- вставь сюда токен бота

logging.basicConfig(level=logging.INFO)

bot = Bot(token=API_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)
dp.middleware.setup(LoggingMiddleware())

# ======== База данных SQLite ========
conn = sqlite3.connect('aurelia_bot.db')
cursor = conn.cursor()

cursor.execute('''
CREATE TABLE IF NOT EXISTS users (
    user_id INTEGER PRIMARY KEY,
    username TEXT,
    subscription INTEGER DEFAULT 0 -- 0 - нет, 1 - есть
)
''')

cursor.execute('''
CREATE TABLE IF NOT EXISTS purchases (
    user_id INTEGER,
    chapter INTEGER,
    PRIMARY KEY (user_id, chapter)
)
''')

conn.commit()

# ======== Клавиатуры ========

main_menu_kb = ReplyKeyboardMarkup(resize_keyboard=True)
main_menu_kb.add(
    KeyboardButton("📖 Читать книгу"),
    KeyboardButton("💳 Магазин"),
    KeyboardButton("⚙️ Настройки"),
)
main_menu_kb.add(
    KeyboardButton("🎲 Викторины"),
    KeyboardButton("🎁 Рефералы"),
    KeyboardButton("💬 Чат с автором"),
)

# ======== Пример данных книги ========
FREE_CHAPTERS = [1, 2, 3]
TOTAL_CHAPTERS = 10

CHAPTERS_TEXT = {
    1: "Глава 1. Предисловие...\n(текст главы...)",
    2: "Глава 2. Начало...\n(текст главы...)",
    3: "Глава 3. Тайны...\n(текст главы...)",
    4: "Глава 4. Закат...\n(текст главы...)",
    # и так далее...
}

# ======== Хелпер для проверки доступа ========
def user_has_access(user_id: int, chapter: int) -> bool:
    if chapter in FREE_CHAPTERS:
        return True
    cursor.execute("SELECT subscription FROM users WHERE user_id=?", (user_id,))
    res = cursor.fetchone()
    if res and res[0] == 1:
        return True
    cursor.execute("SELECT 1 FROM purchases WHERE user_id=? AND chapter=?", (user_id, chapter))
    return cursor.fetchone() is not None

# ======== Хендлеры ========

@dp.message_handler(commands=['start'])
async def cmd_start(message: types.Message):
    user_id = message.from_user.id
    username = message.from_user.username or ""
    cursor.execute("INSERT OR IGNORE INTO users (user_id, username) VALUES (?, ?)", (user_id, username))
    conn.commit()

    await message.answer(
        "Привет! Я AURELIA_Protocol_Bot — твой проводник в мире книги 'Freedom's Chaos'.\n\n"
        "Выбери действие в меню ниже.",
        reply_markup=main_menu_kb
    )

@dp.message_handler(lambda message: message.text == "📖 Читать книгу")
async def read_book_handler(message: types.Message):
    user_id = message.from_user.id
    kb = InlineKeyboardMarkup(row_width=3)
    for chapter in range(1, TOTAL_CHAPTERS + 1):
        if user_has_access(user_id, chapter):
            kb.insert(InlineKeyboardButton(text=f"Глава {chapter}", callback_data=f"chapter_{chapter}"))
        else:
            kb.insert(InlineKeyboardButton(text=f"Глава {chapter} 🔒", callback_data=f"chapter_locked_{chapter}"))
    await message.answer("Выбери главу для чтения:", reply_markup=kb)

@dp.callback_query_handler(lambda c: c.data and c.data.startswith('chapter_'))
async def process_chapter(callback_query: types.CallbackQuery):
    user_id = callback_query.from_user.id
    data = callback_query.data

    if data.startswith("chapter_locked_"):
        chapter = int(data.split('_')[-1])
        await callback_query.answer("Эта глава заблокирована. Купить или оформить подписку можно в магазине.", show_alert=True)
        return

    chapter = int(data.split('_')[-1])
    if user_has_access(user_id, chapter):
        text = CHAPTERS_TEXT.get(chapter, "Глава еще не готова.")
        await callback_query.message.edit_text(text, reply_markup=None)
    else:
        await callback_query.answer("У тебя нет доступа к этой главе.", show_alert=True)

@dp.message_handler(lambda message: message.text == "💳 Магазин")
async def shop_handler(message: types.Message):
    kb = InlineKeyboardMarkup(row_width=2)
    kb.add(
        InlineKeyboardButton("Купить главу 4", callback_data="buy_chapter_4"),
        InlineKeyboardButton("Оформить подписку", callback_data="subscribe")
    )
    await message.answer("Магазин — выбери действие:", reply_markup=kb)

@dp.callback_query_handler(lambda c: c.data and c.data.startswith('buy_chapter_'))
async def buy_chapter_handler(callback_query: types.CallbackQuery):
    user_id = callback_query.from_user.id
    chapter = int(callback_query.data.split('_')[-1])

    # Здесь должна быть интеграция с платежной системой
    # Пока имитируем оплату:
    cursor.execute("INSERT OR IGNORE INTO purchases (user_id, chapter) VALUES (?, ?)", (user_id, chapter))
    conn.commit()

    await callback_query.answer(f"Глава {chapter} куплена! Доступ открыт.", show_alert=True)

@dp.callback_query_handler(lambda c: c.data == 'subscribe')
async def subscribe_handler(callback_query: types.CallbackQuery):
    user_id = callback_query.from_user.id
    cursor.execute("UPDATE users SET subscription=1 WHERE user_id=?", (user_id,))
    conn.commit()

    await callback_query.answer("Подписка оформлена! У тебя полный доступ ко всем главам.", show_alert=True)

@dp.message_handler(lambda message: message.text == "⚙️ Настройки")
async def settings_handler(message: types.Message):
    kb = InlineKeyboardMarkup(row_width=1)
    kb.add(
        InlineKeyboardButton("Настроить рассылку", callback_data="set_schedule"),
        InlineKeyboardButton("Управление подпиской", callback_data="manage_subscription")
    )
    await message.answer("Настройки:", reply_markup=kb)

@dp.callback_query_handler(lambda c: c.data == "set_schedule")
async def set_schedule_handler(callback_query: types.CallbackQuery):
    kb = InlineKeyboardMarkup(row_width=2)
    kb.add(
        InlineKeyboardButton("Ежедневно", callback_data="schedule_daily"),
        InlineKeyboardButton("Раз в неделю", callback_data="schedule_weekly"),
        InlineKeyboardButton("Выключить", callback_data="schedule_off")
    )
    await callback_query.message.answer("Выбери частоту рассылки новых глав:", reply_markup=kb)

@dp.callback_query_handler(lambda c: c.data and c.data.startswith('schedule_'))
async def schedule_choice_handler(callback_query: types.CallbackQuery):
    choice = callback_query.data.split('_')[-1]
    user_id = callback_query.from_user.id
    # Здесь надо сохранить настройку в БД (пока просто ответ)
    await callback_query.answer(f"Рассылка установлена: {choice}", show_alert=True)

@dp.message_handler(lambda message: message.text == "🎲 Викторины")
async def quiz_handler(message: types.Message):
    question = "Кто главный герой книги?"
    answers = ["Аурелия", "Диссиденты", "Лондон", "Паровые машины"]

    kb = InlineKeyboardMarkup(row_width=2)
    for i, ans in enumerate(answers):
        kb.insert(InlineKeyboardButton(ans, callback_data=f"quiz_{i}"))

    await message.answer(question, reply_markup=kb)

@dp.callback_query_handler(lambda c: c.data and c.data.startswith('quiz_'))
async def quiz_answer_handler(callback_query: types.CallbackQuery):
    answer_id = int(callback_query.data.split('_')[-1])
    correct = 0  # индекс правильного ответа
    if answer_id == correct:
        await callback_query.answer("Правильно! 🎉", show_alert=True)
    else:
        await callback_query.answer("Неправильно, попробуй еще.", show_alert=True)

@dp.message_handler(lambda message: message.text == "🎁 Рефералы")
async def referral_handler(message: types.Message):
    user_id = message.from_user.id
    referral_link = f"https://t.me/YOUR_BOT_USERNAME?start={user_id}"
    await message.answer(f"Поделись этой ссылкой и получай бонусы:\n{referral_link}")

@dp.message_handler(lambda message: message.text == "💬 Чат с автором")
async def chat_with_author_handler(message: types.Message):
    await message.answer("Напиши сюда свой вопрос или сообщение автору. Ответ придет в течение 24 часов.")

# ======== Запуск бота ========
async def main():
    await dp.start_polling(skip_updates=True)

if __name__ == '__main__':
    asyncio.run(main())
