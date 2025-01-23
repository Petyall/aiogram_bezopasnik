from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from app.requests import MetricRequests


def url_action_keyboard():
    buttons = [
        [InlineKeyboardButton(text="Проверка на фишинг", callback_data="prediction"), 
         InlineKeyboardButton(text="Получить скриншот", callback_data="screenshot")],
        [InlineKeyboardButton(text="Дешифрование короткой ссылки", callback_data="expansion")]
    ]
    keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
    return(keyboard)


async def get_metrics_keyboard():
    categories = await MetricRequests().find_all()
    keyboard = InlineKeyboardBuilder()
    for category in categories:
        keyboard.add(
            InlineKeyboardButton(
                text=category.name, callback_data=f"category_{category.id}"
            )
        )
    return keyboard.adjust(1).as_markup()


async def get_metrics_cancel_keyboard():
    buttons = [
        [InlineKeyboardButton(text="Назад", callback_data="back_to_categories")],
        [InlineKeyboardButton(text="Отмена", callback_data="cancel_getting_metric")]
    ]
    keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
    return(keyboard)
