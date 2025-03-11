import asyncio
import os

from aiogram import Bot, Dispatcher
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import Message
from dotenv import load_dotenv


class UserInfo(StatesGroup):
    name = State()
    favorite_language = State()


async def command_start(message: Message, state: FSMContext) -> None:
    await state.set_state(UserInfo.name)
    await message.answer("Привет! Как тебя зовут?")


async def process_name(message: Message, state: FSMContext) -> None:
    data = await state.update_data(name=message.text)
    await state.set_state(UserInfo.favorite_language)

    name = data["name"]
    await message.answer(f"{name}, какой у тебя любимый язык программирования?")


async def process_language(message: Message, state: FSMContext) -> None:
    data = await state.update_data(favorite_language=message.text)
    match data["favorite_language"]:
        case "python":
            answer = "Понять и простить"
        case "c#":
            answer = "Это мой любимый язык тоже!"
        case "java":
            answer = "Рекомендую попробовать C# =)"
        case _:
            answer = "Не знаю такого языка =("

    await state.clear()
    await message.answer(answer)


async def main() -> None:
    load_dotenv()
    bot_token = os.getenv("TELEGRAM_BOT_TOKEN")

    dp = Dispatcher()
    dp.message.register(command_start, Command("start"))
    dp.message.register(process_name, UserInfo.name)
    dp.message.register(process_language, UserInfo.favorite_language)

    bot = Bot(token=bot_token)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
