import logging
from aiogram import Bot, Dispatcher, executor, types
import vt
import validators
import os

from screensaver import get_screenshot
from settings import api_key, token
from urldecoding import urldecoding


# ПОДКЛЮЧЕНИЕ К БОТУ ЧЕРЕЗ AIOGRAM
API_TOKEN = token
logging.basicConfig(level=logging.INFO)
bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

# ПОДКЛЮЧЕНИЕ К VIRUSTOTAL API 
client = vt.Client(api_key)

# ФУНКЦИЯ ОБРАБОТКИ КОМАНД /start и /help
@dp.message_handler(commands=['start', 'help'])
async def send_welcome(message: types.Message):
    await message.reply("Привет")

# ФУНКЦИЯ ОБРАБОТКИ КОМАНДЫ /screen
@dp.message_handler(commands=['screen'])
async def screenshot(message: types.Message):
    # ВЗЯТИЕ ССЫЛКИ ИЗ СООБЩЕНИЯ ПОЛЬЗОВАТЕЛЯ
    url = message.get_args()
    # ВАЛИДАЦИЯ ССЫЛКИ ИЗ СООБЩЕНИЯ ПОЛЬЗОВАТЕЛЯ
    if validators.url(url):
        # ВЫЗОВ ФУНКЦИИ ПОЛУЧЕНИЯ СКРИНШОТА
        await get_screenshot(url, message.from_user.username)
        # ОБРАБОТКА ОШИБКИ ПОИСКА СКРИНШОТА
        try:
            # ОТКРЫТИЕ СКРИНШОТА, СОЗДАННОГО ФУНКЦИЕЙ
            with open(f'{message.from_user.username}.png', 'rb') as photo:
                # ОТПРАВКА СКРИНШОТА ПОЛЬЗОВАТЕЛЮ
                await message.reply_photo(photo, caption='Screenshot')
                # УДАЛЕНИЕ СКРИНШОТА ИЗ ПАМЯТИ
                os.remove(f'{message.from_user.username}.png')
        # ЕСЛИ СКРИНШОТ НЕ БЫЛ СОЗДАН, ВЫВЕДЕТСЯ СООБЩЕНИЕ
        except:
            await message.reply("Произошла ошибка :(")
    # ЕСЛИ ССЫЛКА ПОЛЬЗОВАТЕЛЯ НЕ ПРОЙДЕТ ВАЛИДАЦИЮ, ВЫВЕДЕТСЯ СООБЩЕНИЕ
    else:
        await message.reply("❌Ссылка не обнаружена❌\nПример: \n/decoding https://www.SOMETHING.com")

# ФУНКЦИЯ ОБРАБОТКИ КОМАНДЫ /urlscan
@dp.message_handler(commands=['urlscan'])
async def urlscan(message: types.Message):
    # ВЗЯТИЕ ССЫЛКИ ИЗ СООБЩЕНИЯ ПОЛЬЗОВАТЕЛЯ
    url = message.get_args()
    # ВАЛИДАЦИЯ ССЫЛКИ ИЗ СООБЩЕНИЯ ПОЛЬЗОВАТЕЛЯ
    if validators.url(url):
        # ОБРАБОТКА ОШИБКИ ПРОВЕРКИ ССЫЛКИ
        try:
            # СКАНИРОВАНИЕ ССЫЛКИ НА НАЛИЧИЕ ВИРУСОВ ФУНКЦИЕЙ VIRUSTOTAL
            analysis = await vt.Client.scan_url_async(self=client, url=url, wait_for_completion=True)
            # ВЗЯТИЕ ИЗ СЛОВАРЯ КОНКРЕТНОГО ЗНАЧЕНИЯ
            info = analysis.get('stats')
            # ЛОГИКА ДЛЯ ВЫВОДА СООБЩЕНИЯ ПОЛЬЗОВАТЕЛЮ
            result = f'Сайт может быть опасен!\n{info["malicious"]} из 90 антивирусов посчитали этот сайт непригодным :(' if info['malicious'] else 'Сайт безопасен'
            # ОТПРАВКА РЕЗУЛЬТАТОВ ПРОВЕРКИ
            await message.reply(result)
        # ЕСЛИ ССЫЛКА НЕ ПРОШЛА ПРОВЕРКУ, ВЫВЕДЕТСЯ СООБЩЕНИЕ
        except:
            await message.reply("Произошла ошибка :(")
    # ЕСЛИ ССЫЛКА ПОЛЬЗОВАТЕЛЯ НЕ ПРОЙДЕТ ВАЛИДАЦИЮ, ВЫВЕДЕТСЯ СООБЩЕНИЕ
    else:
        await message.reply("❌Ссылка не обнаружена❌\nПример: \n/decoding https://www.SOMETHING.com")

# ФУНКЦИЯ ОБРАБОТКИ КОМАНДЫ /decoding
@dp.message_handler(commands=['decoding'])
async def decoding(message: types.Message):
    # ВЗЯТИЕ ССЫЛКИ ИЗ СООБЩЕНИЯ ПОЛЬЗОВАТЕЛЯ
    url = message.get_args()
    # ВАЛИДАЦИЯ ССЫЛКИ ИЗ СООБЩЕНИЯ ПОЛЬЗОВАТЕЛЯ
    if validators.url(url):
        # ВЫЗОВ ФУНКЦИИ РАСШИФРОВКИ ССЫЛКИ
        context = await urldecoding(url)
        # ОТПРАВКА РЕЗУЛЬТАТОВ РАСШИФРОВКИ
        await message.reply(context)
    # ЕСЛИ ССЫЛКА ПОЛЬЗОВАТЕЛЯ НЕ ПРОЙДЕТ ВАЛИДАЦИЮ, ВЫВЕДЕТСЯ СООБЩЕНИЕ
    else:
        await message.reply("❌Ссылка не обнаружена❌\nПример: \n/decoding https://www.SOMETHING.com")
 

# БЕСКОНЕЧНЫЙ ЦИКЛ РАБОТЫ БОТА
if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=False)