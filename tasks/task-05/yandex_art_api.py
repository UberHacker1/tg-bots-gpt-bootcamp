import os
import time
from base64 import b64decode
from datetime import datetime
from io import BytesIO

import requests
from dotenv import load_dotenv
from PIL import Image

load_dotenv()
folder_id = os.getenv("YANDEX_FOLDER_ID")
api_key = os.getenv("YANDEX_API_KEY")

seed = int(round(datetime.now().timestamp()))
prompt = "Милый пушистый котенок спит на спине. Octane render,f/2.8, ISO 200"

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
image = Image.open(BytesIO(image_bytes))
image.show()
