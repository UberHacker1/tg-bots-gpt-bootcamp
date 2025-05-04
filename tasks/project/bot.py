import asyncio
import requests
from PIL import Image
import os
import time
from base64 import b64decode
from datetime import datetime
from io import BytesIO

from aiogram import Bot, Dispatcher, F
from aiogram.types import Message
from dotenv import load_dotenv

def summarize_text(user_prompt, is_short):
    load_dotenv()
    folder_id = os.getenv("YANDEX_FOLDER_ID")
    api_key = os.getenv("YANDEX_API_KEY")
    gpt_model = 'yandexgpt-lite'

    if is_short: system_prompt = 'Ты должен прислать краткий пересказ текста который ввел пользователь' 
    else: system_prompt = 'Ты должен прислать подробный пересказ текста который ввел пользователь'

    body = {
        'modelUri': f'gpt://{folder_id}/{gpt_model}',
        'completionOptions': {'stream': False, 'temperature': 0.3, 'maxTokens': 2000},
        'messages': [
            {'role': 'system', 'text': system_prompt},
            {'role': 'user', 'text': user_prompt},
        ],
    }
    url = 'https://llm.api.cloud.yandex.net/foundationModels/v1/completionAsync'
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Api-Key {api_key}'
    }

    response = requests.post(url, headers=headers, json=body)
    operation_id = response.json().get('id')

    url = f"https://llm.api.cloud.yandex.net:443/operations/{operation_id}"
    headers = {"Authorization": f"Api-Key {api_key}"}

    while True:
        response = requests.get(url, headers=headers)
        done = response.json()["done"]
        if done:
            break
        time.sleep(2)

    data = response.json()
    answer = data['response']['alternatives'][0]['message']['text']
    return answer 
def generate_image(user_prompt):
    load_dotenv()
    folder_id = os.getenv("YANDEX_FOLDER_ID")
    api_key = os.getenv("YANDEX_API_KEY")

    seed = int(round(datetime.now().timestamp()))
    prompt = user_prompt

    body = {
        "modelUri": f"art://{folder_id}/yandex-art/latest",
        "generationOptions": {"seed": seed, "temperature": 0.6},
        "messages": [
            {"weight": 1, "text": prompt},
        ],
    }
    url = "https://llm.api.cloud.yandex.net/foundationModels/v1/imageGenerationAsync"
    headers = {"Authorization": f"Api-Key {api_key}"}

    response = requests.post(url, headers=headers, json=body)
    operation_id = response.json()["id"]

    url = f"https://llm.api.cloud.yandex.net:443/operations/{operation_id}"
    headers = {"Authorization": f"Api-Key {api_key}"}

    while True:
        response = requests.get(url, headers=headers)
        done = response.json()["done"]
        if done:
            break
        time.sleep(2)

    image_data = response.json()["response"]["image"]
    image_bytes = b64decode(image_data)
    return image_bytes
    

async def bot_ans(message: Message) -> None:
    short_text = f"Краткий пересказ:\n\n{summarize_text(message.text, is_short=1)}"
    long_text = f"Подробный пересказ:\n\n{summarize_text(message.text, is_short=0)}"
    await message.answer(short_text)
    await message.answer(long_text)
    await message.reply_photo(generate_image(short_text[:200]))



async def main() -> None:
    load_dotenv()
    bot_token = os.getenv("TELEGRAM_BOT_TOKEN")

    dp = Dispatcher()
    dp.message.register(bot_ans, F.text)

    bot = Bot(token=bot_token)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())