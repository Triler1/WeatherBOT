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
        await bot.send_message(msg.from_user.id, text=f"<b>✌️ Привет {msg.from_user.first_name}</b>, я 🤖 <b>Погодный Бот</b>!\nЯ могу узнать погоду в любом городе. Просто выберите нужную опцию.", reply_markup=kb, parse_mode='HTML')
    else:
        await bot.send_message(msg.from_user.id, text=f"✌️ Привет <b>{msg.from_user.first_name}</b>, я 🤖 <b>Погодный Бот</b>! Я могу узнать погоду в любом городе. Просто выберите нужную опцию.", reply_markup=kb1, parse_mode='HTML')

@dp.message_handler(Text(equals="Текущая погода"))
async def current_weather(message: types.message):
    await bot.send_message(chat_id=message.from_user.id, text="<i>Введите название города, в котором хотите узнать погоду:</i>", parse_mode='html')
    coll.update_one({"chat_id": message.from_user.id}, {"$set": {"ct": True}})

@dp.message_handler(Text(equals="Прогноз погоды"))
async def schedule_weather(message: types.message):
    await bot.send_message(chat_id=message.from_user.id, text="<i>Выберите количество дней прогноза:</i>", reply_markup=ikb, parse_mode='html')

@dp.message_handler(Text(equals="🔔 Включить уведомление"))
async def schedule_weather(message: types.message):
  for ct in coll.find({"chat_id": message.from_user.id}):
    if (ct['city'] == ""):
        await bot.send_message(chat_id=message.from_user.id, text="<i>Введите название города, уведомления о котором хотите получать:</i>", parse_mode='html')
        coll.update_one({"chat_id": message.from_user.id}, {"$set": {"city": "process"}})
    elif (ct['city'] == "process"):
        await bot.send_message(chat_id=message.from_user.id, text="<i>Введите название города, уведомления о котором хотите получать:</i>", parse_mode='html')
    else:
        await bot.send_message(chat_id=message.from_user.id, text=f"<i>Уведомление уже включено.</i>", reply_markup=kb1)

@dp.message_handler(Text(equals="🔕 Выключить уведомление"))
async def schedule_weather(message: types.message):
  for ct in coll.find({"chat_id": message.from_user.id}):
    notifications = ct['city']
  if (notifications != "" and notifications != "process"):
    scheduler.remove_job(f"{ct['schedule']}")
    coll.update_one({"chat_id": message.from_user.id}, {"$set": {"city": ""}})
    coll.update_one({"chat_id": message.from_user.id}, {"$set": {"schedule": ""}})
    await bot.send_message(chat_id=message.from_user.id, text=f"Уведомление о погоде отключено.", reply_markup=kb)
  else:
    await bot.send_message(chat_id=message.from_user.id, text=f"Включите уведомление.", reply_markup=kb)

@dp.message_handler(Text(equals="💵 Поддержать автора"))
async def buy(message: types.message):
    await bot.send_message(message.chat.id, '📈 Каждый донат мотивирует развивать проект', reply_markup=ikb1)
    
@dp.callback_query_handler(text='1')
async def callback(message: types.Message):
    await bot.delete_message(message.from_user.id, message.message.message_id)
    coll.update_one({"chat_id": message.from_user.id}, {"$set": {"number": 1}})
    await bot.send_message(chat_id=message.from_user.id, text="Введите название города, о котором хотите узнать прогноз погоды:")
    coll.update_one({"chat_id": message.from_user.id}, {"$set": {"forecast": True}})

@dp.callback_query_handler(text='2')
async def callback(message: types.Message):
    await bot.delete_message(message.from_user.id, message.message.message_id)
    coll.update_one({"chat_id": message.from_user.id}, {"$set": {"number": 2}})
    await bot.send_message(chat_id=message.from_user.id, text="Введите название города, о котором хотите узнать прогноз погоды:")
    coll.update_one({"chat_id": message.from_user.id}, {"$set": {"forecast": True}})

@dp.callback_query_handler(text='3')
async def callback(message: types.Message):
    await bot.delete_message(message.from_user.id, message.message.message_id)
    coll.update_one({"chat_id": message.from_user.id}, {"$set": {"number": 3}})
    await bot.send_message(chat_id=message.from_user.id, text="Введите название города, о котором хотите узнать прогноз погоды:")
    coll.update_one({"chat_id": message.from_user.id}, {"$set": {"forecast": True}})

@dp.message_handler()
async def e(message: types.message):
    global notifications
    global ct
    global current
    async def save_weather():
        request = requests.get(f"http://api.weatherapi.com/v1/current.json?key={weather_token}&q={save_city}&lang=ru")
        weather = request.json()
        global emoji
        global dir
        if (weather['current']['condition']['text'] == 'Ясно'):
            emoji = '🌕'
        elif (weather['current']['condition']['text'] == 'Солнечно'):
            emoji = '☀️'
        elif (weather['current']['condition']['text'] == 'Переменная облачность'):
            emoji = '⛅️'
        elif (weather['current']['condition']['text'] == 'Облачно'):
            emoji = '🌥'
        elif (weather['current']['condition']['text'] == 'Пасмурно'):
            emoji = '☁️'
        elif (weather['current']['condition']['text'] == 'Дымка' or weather['current']['condition']['text'] == 'Туман' or weather['current']['condition']['text'] == 'Переохлажденный туман'):
            emoji = '🌫'
        elif (weather['current']['condition']['text'] == 'Местами дождь' or weather['current']['condition']['text'] == 'Местами дождь со снегом' or weather['current']['condition']['text'] == 'Местами замерзающая морось' or weather['current']['condition']['text'] == 'Слабая морось' or weather['current']['condition']['text'] == 'Замерзающая морось' or weather['current']['condition']['text'] == 'Сильная замерзающая морось' or weather['current']['condition']['text'] == 'Местами небольшой дождь' or weather['current']['condition']['text'] == 'Небольшой дождь' or weather['current']['condition']['text'] == 'Временами умеренный дождь' or weather['current']['condition']['text'] == 'Умеренный дождь' or weather['current']['condition']['text'] == 'Временами сильный дождь' or weather['current']['condition']['text'] == 'Сильный дождь' or weather['current']['condition']['text'] == 'Слабый переохлажденный дождь' or weather['current']['condition']['text'] == 'Умеренный или сильный переохлажденный дождь' or weather['current']['condition']['text'] == 'Небольшой дождь со снегом' or weather['current']['condition']['text'] == 'Умеренный или сильный дождь со снегом' or weather['current']['condition']['text'] == 'Небольшой ливневый дождь' or weather['current']['condition']['text'] == 'Умеренный или сильный ливневый дождь' or weather['current']['condition']['text'] == 'Сильные ливни' or weather['current']['condition']['text'] == 'Небольшой ливневый дождь со снегом' or weather['current']['condition']['text'] == 'Умеренные или сильные ливневые дожди со снегом' or weather['current']['condition']['text'] == 'Умеренный или сильный снег' or weather['current']['condition']['text'] == 'Небольшой ледяной дождь' or weather['current']['condition']['text'] == 'Умеренный или сильный ледяной дождь'):
            emoji = '🌧'
        elif (weather['current']['condition']['text'] == 'Местами снег' or weather['current']['condition']['text'] == 'Поземок' or weather['current']['condition']['text'] == 'Метель' or weather['current']['condition']['text'] == 'Местами небольшой снег' or weather['current']['condition']['text'] == 'Небольшой снег' or weather['current']['condition']['text'] == 'Местами умеренный снег' or weather['current']['condition']['text'] == 'Умеренный снег' or weather['current']['condition']['text'] == 'Местами сильный снег' or weather['current']['condition']['text'] == 'Сильный снег' or weather['current']['condition']['text'] == 'Небольшой снег' or weather['current']['condition']['text'] == 'В отдельных районах местами небольшой снег с грозой' or weather['current']['condition']['text'] == 'В отдельных районах умеренный или сильный снег с грозой'):
            emoji = '🌨'
        elif (weather['current']['condition']['text'] == 'Местами грозы'):
            emoji = '🌩'
        else:
            emoji = '⛈'
        if (weather['current']['wind_dir'] == 'SW'
          or weather['current']['wind_dir'] == 'SSW'
          or weather['current']['wind_dir'] == 'WSW'):
            dir = 'ЮЗ'
        elif (weather['current']['wind_dir'] == 'NNE'
            or weather['current']['wind_dir'] == 'NE'
            or weather['current']['wind_dir'] == 'ENE'):
            dir = 'СВ'
        elif (weather['current']['wind_dir'] == 'ESE'
            or weather['current']['wind_dir'] == 'SE'
            or weather['current']['wind_dir'] == 'SSE'):
            dir = 'ЮВ'
        else:
            dir = 'СЗ'
        word = morph.parse(weather['location']['name'])[0]
        loct = word.inflect({'loct'})
        await bot.send_message(chat_id=message.from_user.id, text=
      f"Погода в <b><i>{loct.word.title()}</i></b>.\n{emoji} {weather['current']['condition']['text']}:\n"
      f"🌡 Температура {round(weather['current']['temp_c'])}°C,\n"
      f"💨 Скорость ветра {round(weather['current']['wind_kph'] * 1000 / 3600)} м/c,\n"
      f"💧 Влажность {weather['current']['humidity']}%.\n"
      f"🧭 Направление ветра {dir}", parse_mode="HTML")
    for ct in coll.find({"chat_id": message.from_user.id}):
        current = ct['ct']
        notifications = ct['city']
    if (current):
        try:
            city = message.text
            request = requests.get(f"http://api.weatherapi.com/v1/current.json?key={weather_token}&q={city}&lang=ru")
            weather = request.json()
            global emoji
            global dir
            global morph
            if (weather['current']['condition']['text'] == 'Ясно'):
                emoji = '🌕'
            elif (weather['current']['condition']['text'] == 'Солнечно'):
                emoji = '☀️'
            elif (weather['current']['condition']['text'] == 'Переменная облачность'):
                emoji = '⛅️'
            elif (weather['current']['condition']['text'] == 'Облачно'):
                emoji = '🌥'
            elif (weather['current']['condition']['text'] == 'Пасмурно'):
                emoji = '☁️'
            elif (weather['current']['condition']['text'] == 'Дымка' or weather['current']['condition']['text'] == 'Туман' or weather['current']['condition']['text'] == 'Переохлажденный туман'):
                emoji = '🌫'
            elif (weather['current']['condition']['text'] == 'Местами дождь' or weather['current']['condition']['text'] == 'Местами дождь со снегом' or weather['current']['condition']['text'] == 'Местами замерзающая морось' or weather['current']['condition']['text'] == 'Слабая морось' or weather['current']['condition']['text'] == 'Замерзающая морось' or weather['current']['condition']['text'] == 'Сильная замерзающая морось' or weather['current']['condition']['text'] == 'Местами небольшой дождь' or weather['current']['condition']['text'] == 'Небольшой дождь' or weather['current']['condition']['text'] == 'Временами умеренный дождь' or weather['current']['condition']['text'] == 'Умеренный дождь' or weather['current']['condition']['text'] == 'Временами сильный дождь' or weather['current']['condition']['text'] == 'Сильный дождь' or weather['current']['condition']['text'] == 'Слабый переохлажденный дождь' or weather['current']['condition']['text'] == 'Умеренный или сильный переохлажденный дождь' or weather['current']['condition']['text'] == 'Небольшой дождь со снегом' or weather['current']['condition']['text'] == 'Умеренный или сильный дождь со снегом' or weather['current']['condition']['text'] == 'Небольшой ливневый дождь' or weather['current']['condition']['text'] == 'Умеренный или сильный ливневый дождь' or weather['current']['condition']['text'] == 'Сильные ливни' or weather['current']['condition']['text'] == 'Небольшой ливневый дождь со снегом' or weather['current']['condition']['text'] == 'Умеренные или сильные ливневые дожди со снегом' or weather['current']['condition']['text'] == 'Умеренный или сильный снег' or weather['current']['condition']['text'] == 'Небольшой ледяной дождь' or weather['current']['condition']['text'] == 'Умеренный или сильный ледяной дождь'):
                emoji = '🌧'
            elif (weather['current']['condition']['text'] == 'Местами снег' or weather['current']['condition']['text'] == 'Поземок' or weather['current']['condition']['text'] == 'Метель' or weather['current']['condition']['text'] == 'Местами небольшой снег' or weather['current']['condition']['text'] == 'Небольшой снег' or weather['current']['condition']['text'] == 'Местами умеренный снег' or weather['current']['condition']['text'] == 'Умеренный снег' or weather['current']['condition']['text'] == 'Местами сильный снег' or weather['current']['condition']['text'] == 'Сильный снег' or weather['current']['condition']['text'] == 'Небольшой снег' or weather['current']['condition']['text'] == 'В отдельных районах местами небольшой снег с грозой' or weather['current']['condition']['text'] == 'В отдельных районах умеренный или сильный снег с грозой'):
                emoji = '🌨'
            elif (weather['current']['condition']['text'] == 'Местами грозы'):
                emoji = '🌩'
            else:
                emoji = '⛈'
            if (weather['current']['wind_dir'] == 'SW'
          or weather['current']['wind_dir'] == 'SSW'
          or weather['current']['wind_dir'] == 'WSW'):
                dir = 'ЮЗ'
            elif (weather['current']['wind_dir'] == 'NNE'
            or weather['current']['wind_dir'] == 'NE'
            or weather['current']['wind_dir'] == 'ENE'):
                dir = 'СВ'
            elif (weather['current']['wind_dir'] == 'ESE'
            or
            weather['current']['wind_dir'] == 'SE'
            or weather['current']['wind_dir'] == 'SSE'):
                dir = 'ЮВ'
            else:
                dir = 'СЗ'
            word = morph.parse(weather['location']['name'])[0]
            loct = word.inflect({'loct'})
            if (notifications == "process" or notifications == ""):
                await bot.send_message(chat_id=message.from_user.id, text=
          f"Погода в <b><i>{loct.word.title()}</i></b>.\n{emoji} {weather['current']['condition']['text']}:\n"
          f"🌡 Температура {round(weather['current']['temp_c'])}°C,\n"
          f"💨 Скорость ветра {round(weather['current']['wind_kph'] * 1000 / 3600)} м/c,\n"
          f"💧 Влажность {weather['current']['humidity']}%.\n"
          f"🧭 Направление ветра {dir}", reply_markup=kb, parse_mode="HTML")
            else:
                await bot.send_message(chat_id=message.from_user.id, text=
          f"Погода в <b><i>{loct.word.title()}</i></b>.\n{emoji} {weather['current']['condition']['text']}:\n"
          f"🌡 Температура {round(weather['current']['temp_c'])}°C,\n"
          f"💨 Скорость ветра {round(weather['current']['wind_kph'] * 1000 / 3600)} м/c,\n"
          f"💧 Влажность {weather['current']['humidity']}%.\n"
          f"🧭 Направление ветра {dir}", reply_markup=kb1, parse_mode="HTML")
            ct = ''
            current = False
            coll.update_one({"chat_id": message.from_user.id}, {"$set": {"ct": False}})
        except KeyError:
            await message.answer(text="✖️ Город не найден. Повторите попытку.")
    elif (notifications == "process"):
        save_city = message.text
        request = requests.get(f"http://api.weatherapi.com/v1/current.json?key={weather_token}&q={save_city}&lang=ru")
        weather = request.json()
        try:
            if (weather['error']['code'] == 1006):
                await message.answer(text="✖️Город не найден. Повторите попытку.")
        except KeyError:
            for i in range(100):
                schedule = f'weather{i}'
                for ct in coll.find({"schedule": schedule}):
                    schedule = f'weather{i}'
                if (ct['schedule'] != schedule):
                    scheduler.add_job(save_weather, 'cron', hour=5, start_date=datetime.now(), id=f"{schedule}")
                    notifications = False
                    await bot.send_message(chat_id=message.from_user.id, text="✅ Уведомление о погоде включено.\n🕗 Время уведомления 8:00 по МСК.", reply_markup=kb1)
                    coll.update_one({"chat_id": message.from_user.id}, {"$set": {"city": save_city}})
                    coll.update_one({"chat_id": message.from_user.id}, {"$set": {"schedule": schedule}})
                    break
    elif (ct['forecast']):
        try:
            city = message.text
            request = requests.get(f"http://api.weatherapi.com/v1/forecast.json?key={weather_token}&q={city}&days={ct['number']}&lang=ru")
            weather = request.json()
            word = morph.parse(weather['location']['name'])[0]
            loct = word.inflect({'loct'})
            global declination
            if (ct['number'] == 1):
                declination = 'день'
            else:
                declination = 'дня'
            await bot.send_message(chat_id=message.from_user.id, text=f"Погода в <b>{loct.word.title()}</b> на {ct['number']} {declination}:", parse_mode="HTML")
            for i in weather['forecast']['forecastday']:
                if (i['day']['condition']['text'] == 'Ясно'):
                    emoji = '🌕'
                elif (i['day']['condition']['text'] == 'Солнечно'):
                    emoji = '☀️'
                elif (i['day']['condition']['text'] == 'Переменная облачность'):
                    emoji = '⛅️'
                elif (i['day']['condition']['text'] == 'Облачно'):
                    emoji = '🌥'
                elif (i['day']['condition']['text'] == 'Пасмурно'):
                    emoji = '☁️'
                elif (i['day']['condition']['text'] == 'Дымка' or weather['current']['condition']['text'] == 'Туман' or weather['current']['condition']['text'] == 'Переохлажденный туман'):
                    emoji = '🌫'
                elif (i['day']['condition']['text'] == 'Местами дождь' or i['day']['condition']['text'] == 'Местами дождь со снегом' or i['day']['condition']['text'] == 'Местами замерзающая морось' or i['day']['condition']['text'] == 'Слабая морось' or i['day']['condition']['text'] == 'Замерзающая морось' or i['day']['condition']['text'] == 'Сильная замерзающая морось' or i['day']['condition']['text'] == 'Местами небольшой дождь' or i['day']['condition']['text'] == 'Небольшой дождь' or i['day']['condition']['text'] == 'Временами умеренный дождь' or i['day']['condition']['text'] == 'Умеренный дождь' or i['day']['condition']['text'] == 'Временами сильный дождь' or i['day']['condition']['text'] == 'Сильный дождь' or i['day']['condition']['text'] == 'Слабый переохлажденный дождь' or i['day']['condition']['text'] == 'Умеренный или сильный переохлажденный дождь' or i['day']['condition']['text'] == 'Небольшой дождь со снегом' or i['day']['condition']['text'] == 'Умеренный или сильный дождь со снегом' or i['day']['condition']['text'] == 'Небольшой ливневый дождь' or i['day']['condition']['text'] == 'Умеренный или сильный ливневый дождь' or i['day']['condition']['text'] == 'Сильные ливни' or i['day']['condition']['text'] == 'Небольшой ливневый дождь со снегом' or i['day']['condition']['text'] == 'Умеренные или сильные ливневые дожди со снегом' or i['day']['condition']['text'] == 'Умеренный или сильный снег' or i['day']['condition']['text'] == 'Небольшой ледяной дождь' or i['day']['condition']['text'] == 'Умеренный или сильный ледяной дождь'):
                    emoji = '🌧'
                elif (i['day']['condition']['text'] == 'Местами снег' or i['day']['condition']['text'] == 'Поземок' or i['day']['condition']['text'] == 'Метель' or i['day']['condition']['text'] == 'Местами небольшой снег' or i['day']['condition']['text'] == 'Небольшой снег' or i['day']['condition']['text'] == 'Местами умеренный снег' or i['day']['condition']['text'] == 'Умеренный снег' or i['day']['condition']['text'] == 'Местами сильный снег' or i['day']['condition']['text'] == 'Сильный снег' or i['day']['condition']['text'] == 'Небольшой снег' or i['day']['condition']['text'] == 'В отдельных районах местами небольшой снег с грозой' or i['day']['condition']['text'] == 'В отдельных районах умеренный или сильный снег с грозой'):
                    emoji = '🌨'
                elif (i['day']['condition']['text'] == 'Местами грозы'):
                    emoji = '🌩'
                else:
                    emoji = '⛈'
                await bot.send_message(chat_id=message.from_user.id, text=f"<b><i>{i['date']}</i></b>.\n{emoji} {i['day']['condition']['text']}:\n"
                    f"🌡 Средняя температура {round(i['day']['avgtemp_c'])}°C,\n"
                    f"💨 Максимальная скорость ветра {round(i['day']['maxwind_kph'] * 1000 / 3600)} м/c,\n"
                    f"💧 Средняя влажность {round(i['day']['avghumidity'])}%.", parse_mode="HTML")
            ct = ''
            current = False
            coll.update_one({"chat_id": message.from_user.id}, {"$set": {"forecast": False}})
        except KeyError:
            await message.answer(text="✖️ Город не найден. Повторите попытку.")
    else:
        if (notifications == ""):
            await bot.send_message(chat_id=message.from_user.id, text=f"Выберите нужную функцию.", reply_markup=kb)
        else:
            await bot.send_message(chat_id=message.from_user.id, text=f"Выберите нужную функцию.", reply_markup=kb1)

if __name__ == '__main__':
    executor.start_polling(dp, on_startup=on_startup)



if __name__ == '__main__':
    executor.start_polling(dp)
