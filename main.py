import asyncio
import logging
import sys
from os import getenv
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram import Bot, Dispatcher, html
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart
from aiogram.types import Message, CallbackQuery, FSInputFile
from dotenv import load_dotenv
from aiogram.fsm.state import State, StatesGroup
import re
from aiogram.fsm.context import FSMContext
from url_screensaver import take_screenshot
import time
import os
from url_prediction import url_prediction
from joblib import load
from url_expansion import get_long_url



load_dotenv()

TOKEN = getenv("BOT_TOKEN")

dp = Dispatcher()

def url_action_keyboard():
    buttons = [
        [InlineKeyboardButton(text="Проверка на фишинг", callback_data="prediction"), 
         InlineKeyboardButton(text="Получить скриншот", callback_data="screenshot")],
        [InlineKeyboardButton(text="Дешифрование короткой ссылки", callback_data="expansion")]
    ]
    keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
    return(keyboard)

class PhishingPredictionStates(StatesGroup):
    ENTER_VALUE = State()


URL_PATTERN = re.compile(
    r"https?://(?:www\.)?[a-zA-Z0-9-]+\.[a-zA-Z]{2,}(?:/[^\s]*)?"
)

@dp.message()
async def check_message(message: Message, state: FSMContext):
    match = URL_PATTERN.search(message.text)
    if match:
        link = match.group()
        await state.set_state(PhishingPredictionStates.ENTER_VALUE)
        await state.update_data(link=link)
        keyboard = url_action_keyboard()
        await message.answer(f"Что вы хотите сделать с этой ссылкой?: {link}", reply_markup=keyboard)
    else:
        await message.reply("В вашем сообщении нет ссылки.")


@dp.callback_query(lambda c: c.data == 'screenshot', PhishingPredictionStates.ENTER_VALUE)
async def process_get_screenshot(callback_query: CallbackQuery, state: FSMContext):
    user_data = await state.get_data()
    link = user_data.get("link")
    
    await callback_query.bot.edit_message_text(
        chat_id=callback_query.from_user.id,
        message_id=callback_query.message.message_id,
        text="Ожидайте..."
    )
    
    try:
        filename = f'screenshot_{time.time()}.png'
        await take_screenshot(link, filename)
        screenshot = FSInputFile(filename)
        await callback_query.bot.send_photo(
            chat_id=callback_query.from_user.id,
            photo=screenshot,
        )

        await callback_query.bot.delete_message(chat_id=callback_query.from_user.id,
            message_id=callback_query.message.message_id,)

        await callback_query.bot.send_message(
            chat_id=callback_query.from_user.id,
            text=f"Скриншот для: {link}"
        )

    except Exception as e:
        await callback_query.bot.send_message(
            chat_id=callback_query.from_user.id,
            text=f"Произошла ошибка при создании скриншота: {str(e)}"
        )

    finally:
        if os.path.exists(filename):
            os.remove(filename)
        await state.clear()

@dp.callback_query(lambda c: c.data == 'prediction', PhishingPredictionStates.ENTER_VALUE)
async def process_get_prediction(callback_query: CallbackQuery, state: FSMContext):
    user_data = await state.get_data()
    link = user_data.get("link")

    await callback_query.bot.edit_message_text(
        chat_id=callback_query.from_user.id,
        message_id=callback_query.message.message_id,
        text="Ожидайте..."
    )

    try:
        results, file_name = url_prediction(link)
        
        full_path = f"/bezopasnik/{file_name}"
        print(full_path)

        await callback_query.bot.edit_message_text(
            chat_id=callback_query.from_user.id,
            message_id=callback_query.message.message_id,
            text=results
        )

        screenshot_file_name = f'screenshot_{time.time()}.png'
        await take_screenshot(full_path, screenshot_file_name)

        screenshot = FSInputFile(screenshot_file_name)
        await callback_query.bot.send_photo(
            chat_id=callback_query.from_user.id,
            photo=screenshot,
        )

        for filename in (screenshot_file_name, file_name):
            if os.path.exists(filename):
                os.remove(filename)

    except Exception as e:
        await callback_query.bot.send_message(
            chat_id=callback_query.from_user.id,
            text=f"Произошла ошибка при предсказании: {str(e)}"
        )

    finally:
        await state.clear()

@dp.callback_query(lambda c: c.data == 'expansion', PhishingPredictionStates.ENTER_VALUE)
async def process_url_expansion(callback_query: CallbackQuery, state: FSMContext):
    user_data = await state.get_data()
    link = user_data.get("link")

    await callback_query.bot.edit_message_text(
        chat_id=callback_query.from_user.id,
        message_id=callback_query.message.message_id,
        text="Ожидайте..."
    )

    try:
        results = await get_long_url(link)
        await callback_query.bot.edit_message_text(
            chat_id=callback_query.from_user.id,
            message_id=callback_query.message.message_id,
            text=results
        )
    except Exception as e:
        await callback_query.bot.send_message(
            chat_id=callback_query.from_user.id,
            text=f"Произошла ошибка при предсказании: {str(e)}"
        )

    finally:
        await state.clear()

async def main() -> None:

    bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))

    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())