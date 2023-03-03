"""
This is a echo bot.
It echoes any incoming text messages.
"""

import logging

from aiogram import Bot, Dispatcher, executor, types
from settings import token
from screensaver import get_screenshot
import validators
import os

import vt
from settings import api_key


client = vt.Client(api_key)

API_TOKEN = token

logging.basicConfig(level=logging.INFO)

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)


@dp.message_handler(commands=['start', 'help'])
async def send_welcome(message: types.Message):
    await message.reply("Hi!\nI'm EchoBot!\nPowered by aiogram.")


@dp.message_handler(commands=['screen'])
async def screenshot(message: types.Message):
    url = message.get_args()
    if validators.url(url):
        await get_screenshot(url, message.from_user.username)
        with open(f'{message.from_user.username}.png', 'rb') as photo:
            await message.reply_photo(photo, caption='Screenshot')
            os.remove(f'{message.from_user.username}.png')
    else:
        await message.reply("Ссылка не обнаружена")


@dp.message_handler(commands=['urlscan'])
async def urlscan(message: types.Message):
    url = message.get_args()
    if validators.url(url):
        analysis = await vt.Client.scan_url_async(self=client, url=url, wait_for_completion=True)
        info = analysis.get('stats')
        result = f'Сайт может быть опасен!\n{info["malicious"]} из 90 антивирусов посчитали этот сайт непригодным :(' if info['malicious'] else 'Сайт безопасен'
        await message.reply(result)
    else:
        await message.reply("Ссылка не обнаружена")



if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)