import requests

from aiogram import Bot, Dispatcher, executor, types

WEATHER_TOKEN = '<WEATHER-TOKEN>'
API_TOKEN = '<BOT-TOKEN>'

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

@dp.message_handler(commands=['start'])
async def start_command(message: types.message):
    await message.answer(
        text="Привет, я WeatherBOT! Я могу узнать погоду в любом городе. Просто напиши название города.")

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
