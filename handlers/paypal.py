from aiogram import types

def register_handlers(dp):
    dp.message_handler(commands=["paypal"])(paypal_command)
    
async def paypal_command(message: types.Message):
    await message.answer("Команда PayPal принята!")

# Пример HTTP-обработчиков для webhook PayPal (aiohttp handlers)

async def paypal_success(request):
    # логика для успешного платежа
    return web.Response(text="Paypal Success")

async def paypal_cancel(request):
    # логика для отмены платежа
    return web.Response(text="Paypal Cancel")
