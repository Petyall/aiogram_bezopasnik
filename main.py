import sys
import asyncio
import logging

from os import getenv
from dotenv import load_dotenv
from aiogram.types import Message
from aiogram.enums import ParseMode
from aiogram import Bot, Dispatcher
from aiogram.filters import CommandStart
from aiogram.client.default import DefaultBotProperties

from app.handlers import bezopasnik_router
from app.middleware import AlbumMiddleware
from app.requests import AnswerRequests


load_dotenv()

TOKEN = getenv("BOT_TOKEN")

dp = Dispatcher()

dp.message.middleware(AlbumMiddleware())

@dp.message(CommandStart())
async def command_start_handler(message: Message) -> None:
    answer = await AnswerRequests.find_one_or_none(name='start')
    await message.answer(
        f"Привет, *{message.from_user.full_name}*!\n\n{answer.description}"
    )


async def main() -> None:
    bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.MARKDOWN))
    dp.include_router(bezopasnik_router)
    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())
