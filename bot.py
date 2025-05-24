from telegram import Update, KeyboardButton, ReplyKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
import requests
from dotenv import load_dotenv
import os

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
WEATHER_API_KEY = os.getenv("WEATHER_API_KEY")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    button = KeyboardButton("Send Location 📍", request_location=True)
    markup = ReplyKeyboardMarkup([[button]], one_time_keyboard=True, resize_keyboard=True)
    await update.message.reply_text(
        "Hi! You can either:\n1. Share your location 📍\n2. Type your city name, state, and country (e.g., 'Paris, Île-de-France, France')",
        reply_markup=markup
    )

async def location_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    lat = update.message.location.latitude
    lon = update.message.location.longitude
    url = f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={WEATHER_API_KEY}&units=metric"

    response = requests.get(url).json()
    if response.get("cod") != 200:
        await update.message.reply_text("Sorry, couldn't fetch weather. Please try again.")
        return

    weather = response['weather'][0]['description']
    temp = response['main']['temp']
    await update.message.reply_text(f"📍 Location-Based Weather:\nWeather: {weather}\nTemperature: {temp}°C")

async def city_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    city_input = update.message.text
    url = f"https://api.openweathermap.org/data/2.5/weather?q={city_input}&appid={WEATHER_API_KEY}&units=metric"

    response = requests.get(url).json()
    if response.get("cod") != 200:
        await update.message.reply_text("Sorry, couldn't find weather for that location. Please try again.")
        return

    weather = response['weather'][0]['description']
    temp = response['main']['temp']
    city = response['name']
    country = response['sys']['country']
    await update.message.reply_text(f"🌆 Weather in {city}, {country}:\nWeather: {weather}\nTemperature: {temp}°C")

if __name__ == '__main__':
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler('start', start))
    app.add_handler(MessageHandler(filters.LOCATION, location_handler))
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), city_handler))
    app.run_polling()
