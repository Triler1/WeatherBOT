import requests
from aiogram import Bot, Dispatcher, executor, types
from aiogram.dispatcher.filters import Text

import pymongo
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from datetime import datetime

import pymorphy2
from apscheduler.schedulers.asyncio import AsyncIOScheduler

WEATHER_TOKEN = '<WEATHER-TOKEN>'
API_TOKEN = '<BOT-TOKEN>'

client = pymongo.MongoClient('MONGO(')
db = client.test
coll = db.users

bot = Bot(bot_token)
dp = Dispatcher(bot)

morph = pymorphy2.MorphAnalyzer()

notifications = False
current = False

ct = ''
weather = ''
emoji = ''
dir = ''
save_city = ''
value = ''
declination = ''

kb = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
kb.add(KeyboardButton('Текущая погода'))
kb.add(KeyboardButton("Прогноз погоды"))
kb.add(KeyboardButton("🔔 Включить уведомление"))
kb.add(KeyboardButton('💵 Поддержать автора'))

kb1 = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
kb1.add(KeyboardButton('Текущая погода'))
kb1.add(KeyboardButton("Прогноз погоды"))
kb1.add(KeyboardButton('🔕 Выключить уведомление'))
kb1.add(KeyboardButton('💵 Поддержать автора'))

ikb = InlineKeyboardMarkup(row_width=3)

ikb.add(InlineKeyboardButton(text='1', callback_data='1'))
ikb.insert(InlineKeyboardButton(text='2', callback_data='2'))
ikb.insert(InlineKeyboardButton(text='3', callback_data='3'))

ikb1 = InlineKeyboardMarkup(row_width=1)

ikb1.add(InlineKeyboardButton(text='DonationAlerts', url="https://www.donationalerts.com/r/triler2"))

scheduler = AsyncIOScheduler()
scheduler.start()

async def on_startup(dispatcher):
    for value in coll.find():
        break

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)


@dp.message_handler(commands=['start'])
async def start_command(msg: types.message):
    global value
    global notifications
    value = ''
    for value in coll.find({"chat_id": msg.from_user.id}):
        notifications = value['city']
    await bot.send_sticker(msg.from_user.id, "CAACAgIAAxkBAAM9YXfH5sCS-41cwfqE5wF6I25R3U4AAqkRAALI5XFJY-8zAfzb5vghBA")
    if (value == ''):
        coll.insert_one({"chat_id": msg.from_user.id, "city": save_city, "ct": False, "schedule": "", "number": 0, "forecast": False})
    if (notifications == ""):
        await bot.send_message(msg.from_user.id, text=f"👋 Привет <b>{msg.from_user.first_name}</b>, я 🤖 <b>Погодный Бот</b>! Я могу узнать погоду в любом городе. Просто выберите нужную опцию.", reply_markup=kb, parse_mode='HTML')
    else:
        await bot.send_message(msg.from_user.id, text=f"👋 Привет <b>{msg.from_user.first_name}</b>, я 🤖 <b>Погодный Бот</b>! Я могу узнать погоду в любом городе. Просто выберите нужную опцию.", reply_markup=kb1, parse_mode='HTML')

@dp.message_handler()
async def now_weather(message: types.message):
    try:
        city = message.text
        request = requests.get(f"http://api.weatherapi.com/v1/current.json?key={WEATHER_TOKEN}&q={city}&lang=ru")
        weather = request.json()
        await message.answer(
            text=f"Погода: {weather['location']['name']}.\n{weather['current']['condition']['text']}.\n"
                 f"Температура {round(weather['current']['temp_c'])}°C.\n"
                 f"Скорость ветра {round(weather['current']['wind_kph'] * 1000 / 3600)} м/c.\n"
                 f"Влажность {weather['current']['humidity']}%.")
    except KeyError:
        await message.answer(text="Город не найден.")


if __name__ == '__main__':
    executor.start_polling(dp)
