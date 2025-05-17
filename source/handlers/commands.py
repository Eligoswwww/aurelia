from aiogram import types
from aiogram.dispatcher.filters.builtin import CommandStart, CommandHelp
from loader import dp
from keyboards.reply import main_menu

@dp.message_handler(CommandStart())
async def cmd_start(message: types.Message):
    await message.answer('Добро пожаловать в Aurelia Bot!', reply_markup=main_menu())

@dp.message_handler(CommandHelp())
async def cmd_help(message: types.Message):
    await message.answer('Помощь: Вы можете читать главы, купить подписку и т.д.')
