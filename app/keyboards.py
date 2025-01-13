from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


def url_action_keyboard():
    buttons = [
        [InlineKeyboardButton(text="Проверка на фишинг", callback_data="prediction"), 
         InlineKeyboardButton(text="Получить скриншот", callback_data="screenshot")],
        [InlineKeyboardButton(text="Дешифрование короткой ссылки", callback_data="expansion")]
    ]
    keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
    return(keyboard)
