import os
from aiogram import Bot, Dispatcher, F
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.filters import Command
import asyncio
import logging

# ✅ Получаем токен безопасно из переменной окружения
BOT_TOKEN = os.getenv("BOT_TOKEN")

# 🔗 URL твоей Mini App (замени на свой)
WEB_APP_URL = "https://tile-calc-app.replit.app"

# 🤖 Настройка логов и бота
logging.basicConfig(level=logging.INFO)
bot = Bot(token=BOT_TOKEN, parse_mode=ParseMode.HTML)
dp = Dispatcher(storage=MemoryStorage())

@dp.message(Command("start"))
async def cmd_start(message: Message):
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(
                text="🧮 Открыть калькулятор плитки",
                web_app=WebAppInfo(url=WEB_APP_URL)
            )]
        ]
    )
    await message.answer("Привет! Нажми кнопку ниже, чтобы открыть калькулятор 👇", reply_markup=keyboard)

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
