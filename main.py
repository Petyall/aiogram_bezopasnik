import logging
from aiogram import Bot, Dispatcher, executor, types
import vt
import validators
import os
import re

from screensaver import get_screenshot
from settings import api_key, token
from urldecoding import urldecoding
from qrreader import qrreader
from passwordvalidator import is_strong_password

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
            await message.reply("Произошла непредвиденная ошибка, сообщите моему создателю @petyal :(")
    # ЕСЛИ ССЫЛКА ПОЛЬЗОВАТЕЛЯ НЕ ПРОЙДЕТ ВАЛИДАЦИЮ, ВЫВЕДЕТСЯ СООБЩЕНИЕ
    else:
        await message.reply("❌Ссылка не обнаружена❌\nПример: \n/decoding https://www.SOMETHING.com")

# ФУНКЦИЯ ОБРАБОТКИ КОМАНДЫ /urlscan
@dp.message_handler(commands=['urlscan'])
async def urlscan(message: types.Message):
    # ВЗЯТИЕ ССЫЛКИ ИЗ СООБЩЕНИЯ ПОЛЬЗОВАТЕЛЯ
    url = message.get_args()
    # ВАЛИДАЦИЯ ССЫЛКИ ИЗ СООБЩЕНИЯ ПОЛЬЗОВАТЕЛЯ
    if re.match(r'^https://', url):
        https_validate = ''
    else:
        https_validate = "❌Осторожно❌ Ссылка не содержит безопасное подключение https!"
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
            await message.reply(f'{result}\n{https_validate}')
        # ЕСЛИ ССЫЛКА НЕ ПРОШЛА ПРОВЕРКУ, ВЫВЕДЕТСЯ СООБЩЕНИЕ
        except:
            await message.reply("Произошла непредвиденная ошибка, сообщите моему создателю @petyal :(")
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

# ФУНКЦИЯ ДЛЯ РАСШИФРОВКИ QR 
@dp.message_handler(content_types=['photo'])
async def save_photo(message: types.Message):
    # ПОЛУЧЕНИЕ ФОТОГРАФИИ
    photo = message.photo[-1]
    # ГЕНЕРАЦИЯ УНИКАЛЬНОГО ИМЕНИ ДЛЯ ФОТО
    file_name = f"{photo.file_id}.jpg"
    # СОЗДАНИЕ ПАПКИ НА СЕРВЕРЕ
    if not os.path.exists("photos"):
        os.makedirs("photos")
    # ПУТЬ ДО ФАЙЛА И ЕГО НАЗВАНИЕ
    file_path = os.path.join("photos", file_name)
    # ВЫЗОВ ФУНКЦИИ РАСШИФРОВКИ QR
    await photo.download(file_path)
    # ОТПРАВКА РЕЗУЛЬТАТОВ РАСШИФРОВКИ
    await message.reply(await qrreader(file_path))

# ФУНКЦИЯ ОБРАБОТКИ КОМАНДЫ /password 
@dp.message_handler(commands=['password'])
async def delete_message(message: types.Message):
    # ПОЛУЧЕНИЕ ПАРОЛЯ
    password = message.get_args()
    # ВЫЗОВ ФУНКЦИИ ПРОВЕРКИ ПАРОЛЯ И ОТПРАВКА РЕЗУЛЬТАТА
    await bot.send_message(message.chat.id, await is_strong_password(password))
    # УДАЛЕНИЕ СООБЩЕНИЯ, СОДЕРЖАЩЕГО ПАРОЛЬ
    await bot.delete_message(message.chat.id, message.message_id)

# БЕСКОНЕЧНЫЙ ЦИКЛ РАБОТЫ БОТА
if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=False)