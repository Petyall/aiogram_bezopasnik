import re
import os
import time

from dotenv import load_dotenv
from aiogram import Router, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery, FSInputFile

from app.requests import MetricRequests
from app.states import PhishingPredictionStates, GetMetricStates
from app.keyboards import url_action_keyboard, get_metrics_keyboard, get_metrics_cancel_keyboard
from utils.qr_reader import decode_qr
from utils.url_expansion import get_long_url
from utils.url_prediction import url_prediction
from utils.url_screensaver import take_screenshot


load_dotenv()

bezopasnik_router = Router()

URL_PATTERN = re.compile(
    r"https?://(?:www\.)?[a-zA-Z0-9-]+\.[a-zA-Z0-9.-]+(?:/[^\s]*)?"
)


@bezopasnik_router.message(Command("metrics"))
async def cmd_metrics(message: Message, state: FSMContext):
    await state.set_state(GetMetricStates.SELECT_CATEGORY)
    keyboard = await get_metrics_keyboard()
    await message.reply(
        f"Выберите интересующую категорию параметров проверки:", reply_markup=keyboard
    )


@bezopasnik_router.callback_query(lambda c: c.data.startswith("category_"), GetMetricStates.SELECT_CATEGORY)
async def get_metric_process_select_category(callback_query: CallbackQuery, state: FSMContext):
    category_id = int(callback_query.data.split("_")[1])
    selected_category = await MetricRequests.find_one_or_none(id=category_id)

    await state.set_state(GetMetricStates.SELECT_METRIC)

    keyboard = await get_metrics_cancel_keyboard()
    await callback_query.bot.edit_message_text(
        chat_id=callback_query.from_user.id,
        message_id=callback_query.message.message_id,
        text=f"{selected_category.description}",
        reply_markup=keyboard,
    )


@bezopasnik_router.callback_query(lambda c: c.data == "cancel_getting_metric")
async def get_metric_process_cancel(callback_query: CallbackQuery, state: FSMContext):
    await state.clear()
    await callback_query.bot.edit_message_text(
        chat_id=callback_query.from_user.id,
        message_id=callback_query.message.message_id,
        text="Просмотр параметров проверки завершен",
    )


@bezopasnik_router.callback_query(lambda c: c.data == "back_to_categories")
async def get_metric_process_back_to_categories(callback_query: CallbackQuery, state: FSMContext):
    await state.set_state(GetMetricStates.SELECT_CATEGORY)

    keyboard = await get_metrics_keyboard()
    await callback_query.bot.edit_message_text(
        chat_id=callback_query.from_user.id,
        message_id=callback_query.message.message_id,
        text=f"Выберите интересующую категорию параметров проверки:",
        reply_markup=keyboard,
    )


@bezopasnik_router.message(F.text)
async def check_message(message: Message, state: FSMContext):
    match = URL_PATTERN.search(message.text)
    if match:
        link = match.group()
        await state.set_state(PhishingPredictionStates.ENTER_VALUE)
        await state.update_data(link=link)
        keyboard = url_action_keyboard()
        await message.reply(f"Что я могу сделать с этой ссылкой?\n{link}", reply_markup=keyboard)
    else:
        await message.reply("В вашем сообщении нет ссылки :(")


@bezopasnik_router.callback_query(lambda c: c.data == 'screenshot', PhishingPredictionStates.ENTER_VALUE)
async def process_get_screenshot(callback_query: CallbackQuery, state: FSMContext):
    user_data = await state.get_data()
    link = user_data.get("link")
    await callback_query.bot.edit_message_text(
        chat_id=callback_query.from_user.id,
        message_id=callback_query.message.message_id,
        text="Ожидайте..."
    )
    filename = f'screenshot_{time.time()}.png'
    try:
        await take_screenshot(link, filename)
        screenshot = FSInputFile(filename)
        await callback_query.bot.send_photo(
            chat_id=callback_query.from_user.id,
            photo=screenshot
        )
        await callback_query.bot.delete_message(
            chat_id=callback_query.from_user.id,
            message_id=callback_query.message.message_id
        )
        await callback_query.bot.send_message(
            chat_id=callback_query.from_user.id,
            text=f"Скриншот для: {link}"
        )
    except Exception as e:
        await callback_query.bot.send_message(
            chat_id=callback_query.from_user.id,
            text=f"Произошла ошибка при создании скриншота: {e}"
        )
    finally:
        if os.path.exists(filename):
            os.remove(filename)
        await state.clear()


@bezopasnik_router.callback_query(lambda c: c.data == 'prediction', PhishingPredictionStates.ENTER_VALUE)
async def process_get_prediction(callback_query: CallbackQuery, state: FSMContext):
    user_data = await state.get_data()
    link = user_data.get("link")
    await callback_query.bot.edit_message_text(
        chat_id=callback_query.from_user.id,
        message_id=callback_query.message.message_id,
        text="Ожидайте..."
    )
    try:
        results, file_name = await url_prediction(link)
        full_path = os.getenv('FULL_PATH') + file_name
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
            photo=screenshot
        )
        for filename in (screenshot_file_name, file_name):
            if os.path.exists(filename):
                os.remove(filename)
    except Exception as e:
        await callback_query.bot.send_message(
            chat_id=callback_query.from_user.id,
            text=f"Произошла ошибка при предсказании: {e}"
        )
    finally:
        await state.clear()


@bezopasnik_router.callback_query(lambda c: c.data == 'expansion', PhishingPredictionStates.ENTER_VALUE)
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
            text=f"Произошла ошибка при предсказании: {e}"
        )
    finally:
        await state.clear()


async def process_qr_code(message: Message, file_id: str, index: int = None):
    file = await message.bot.get_file(file_id)
    file_name = f"qr_{time.time()}.png"
    file_path = file.file_path

    await message.bot.download_file(file_path, file_name)
    try:
        results = await decode_qr(file_name)
        if results:
            reply_text = f"На изображении {index} найден QR-код:\n{results}" if index else f"На изображении найден QR-код:\n{results}"
        else:
            reply_text = f"На изображении {index} не найден QR-код :(" if index else "На изображении не найден QR-код :("
        await message.reply(reply_text)
    finally:
        os.remove(file_name)


@bezopasnik_router.message(F.photo)
async def qr_reader(message: Message, album: list[Message] = None):
    if album:
        for i, msg in enumerate(album, start=1):
            await process_qr_code(message, msg.photo[-1].file_id, index=i)
    else:
        await process_qr_code(message, message.photo[-1].file_id)
