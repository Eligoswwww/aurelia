import os
import requests
import logging
from aiogram import types, Dispatcher

HF_TOKEN = os.getenv("HF_TOKEN")
MODEL_ID = "Vikhrmodels/Vikhr-Nemo-12B-Instruct-R-21-09-24"

headers = {
    "Authorization": f"Bearer {HF_TOKEN}"
}

logger = logging.getLogger(__name__)

def query_huggingface(payload):
    url = f"https://api-inference.huggingface.co/models/{MODEL_ID}"
    try:
        response = requests.post(url, headers=headers, json=payload, timeout=30)
        logger.info(f"HTTP status: {response.status_code}")
        logger.info(f"Response text: '{response.text}'")
        if response.status_code != 200:
            return {"error": f"HTTP {response.status_code}: {response.text}"}
        return response.json()
    except Exception as e:
        logger.error(f"Ошибка при запросе к Huggingface: {e}")
        return {"error": str(e)}

async def nemo_command(message: types.Message):
    prompt = message.text.strip()
    if not prompt:
        await message.answer("✍️ Пожалуйста, напишите что-нибудь, чтобы я ответил.")
        return

    await message.answer("🤖 Думаю...")

    result = query_huggingface({"inputs": prompt})

    if isinstance(result, list) and "generated_text" in result[0]:
        answer = result[0]["generated_text"]
    elif "generated_text" in result:
        answer = result["generated_text"]
    elif "error" in result:
        answer = f"❌ Ошибка: {result['error']}"
    else:
        answer = "⚠️ Модель не вернула ответ."

    await message.answer(answer)

def register_handlers(dp: Dispatcher):
    # Регистрируем обработчик на все текстовые сообщения
    dp.message.register(nemo_command)

import logging
logger = logging.getLogger(__name__)

async def nemo_command(message: types.Message):
    logger.info(f"Received message: {message.text}")
    ...
