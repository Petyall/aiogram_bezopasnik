import logging
from aiogram import Bot, Dispatcher, executor, types
import vt
import validators
import os
import re
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.contrib.fsm_storage.memory import MemoryStorage

from screensaver import get_screenshot
from settings import api_key, token
from urldecoding import urldecoding
from qrreader import qrreader
from passwordvalidator import is_strong_password

# ПОДКЛЮЧЕНИЕ К БОТУ ЧЕРЕЗ AIOGRAM
API_TOKEN = token
logging.basicConfig(level=logging.INFO)
bot = Bot(token=API_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)

# ПОДКЛЮЧЕНИЕ К VIRUSTOTAL API 
client = vt.Client(api_key)

# ФУНКЦИЯ ОБРАБОТКИ КОМАНД /start и /help
@dp.message_handler(commands=['start', 'help'])
async def send_welcome(message: types.Message):
    await message.reply(f"Привет, {message.from_user.username} ✋!\nЯ - бот-ассистент безопасник 🦾\nМеня наделили способностью проверять ссылки на наличие вирусов, расшифровывать короткие ссылки и QR коды, а также проверять пароль на стойкость к взлому.\nЕсли стало интересно - открывай меню и я помогу тебе ☺️")


class ScreenForm(StatesGroup):
    url = State()

@dp.message_handler(commands='screen')
async def cmd_screen(message: types.Message):
    await ScreenForm.url.set()
    await message.reply("Отправь ссылку")

@dp.message_handler(state=ScreenForm.url)
async def process_screen(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['url'] = message.text
        # ВАЛИДАЦИЯ ССЫЛКИ ИЗ СООБЩЕНИЯ ПОЛЬЗОВАТЕЛЯ
        if validators.url(data['url']):
            # ВЫЗОВ ФУНКЦИИ ПОЛУЧЕНИЯ СКРИНШОТА
            await get_screenshot(data['url'], message.from_user.username)
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

    # завершаем диалог
    await state.finish()


class URLScanForm(StatesGroup):
    url = State()

@dp.message_handler(commands='urlscan')
async def cmd_urlscan(message: types.Message):
    await URLScanForm.url.set()
    await message.reply("Отправь ссылку")

@dp.message_handler(state=URLScanForm.url)
async def process_urlscan(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['url'] = message.text
        if re.match(r'^https://', data['url']):
            https_validate = ''
        else:
            https_validate = "❌Осторожно❌ Ссылка не содержит безопасное подключение https!"
        if validators.url(data['url']):
            # ОБРАБОТКА ОШИБКИ ПРОВЕРКИ ССЫЛКИ
            try:
                # СКАНИРОВАНИЕ ССЫЛКИ НА НАЛИЧИЕ ВИРУСОВ ФУНКЦИЕЙ VIRUSTOTAL
                analysis = await vt.Client.scan_url_async(self=client, url=data['url'], wait_for_completion=True)
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

    # завершаем диалог
    await state.finish()


class URLDecodeForm(StatesGroup):
    url = State()

@dp.message_handler(commands='decoding')
async def cmd_decoding(message: types.Message):
    await URLDecodeForm.url.set()
    await message.reply("Отправь ссылку")

@dp.message_handler(state=URLDecodeForm.url)
async def process_decoding(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['url'] = message.text
        # ВАЛИДАЦИЯ ССЫЛКИ ИЗ СООБЩЕНИЯ ПОЛЬЗОВАТЕЛЯ
        if validators.url(data['url']):
            # ВЫЗОВ ФУНКЦИИ РАСШИФРОВКИ ССЫЛКИ
            context = await urldecoding(data['url'])
            # ОТПРАВКА РЕЗУЛЬТАТОВ РАСШИФРОВКИ
            await message.reply(context)
        # ЕСЛИ ССЫЛКА ПОЛЬЗОВАТЕЛЯ НЕ ПРОЙДЕТ ВАЛИДАЦИЮ, ВЫВЕДЕТСЯ СООБЩЕНИЕ
        else:
            await message.reply("❌Ссылка не обнаружена❌\nПример: \n/decoding https://www.SOMETHING.com")

    # завершаем диалог
    await state.finish()


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



class PasswordForm(StatesGroup):
    password = State()

@dp.message_handler(commands='password')
async def cmd_password(message: types.Message):
    await PasswordForm.password.set()
    await message.reply("Пришли пароль для проверки")

@dp.message_handler(state=PasswordForm.password)
async def process_password(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['password'] = message.text
        # ВЫЗОВ ФУНКЦИИ ПРОВЕРКИ ПАРОЛЯ И ОТПРАВКА РЕЗУЛЬТАТА
        await bot.send_message(message.chat.id, await is_strong_password(data['password']))
        # УДАЛЕНИЕ СООБЩЕНИЯ, СОДЕРЖАЩЕГО ПАРОЛЬ
        await bot.delete_message(message.chat.id, message.message_id)

    # завершаем диалог
    await state.finish()


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    executor.start_polling(dp, skip_updates=True)