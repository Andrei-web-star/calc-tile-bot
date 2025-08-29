import os
import asyncio
from aiogram import Bot, Dispatcher, F
from aiogram.enums import ParseMode
from aiogram.types import Message, WebAppInfo, ReplyKeyboardMarkup, KeyboardButton
from aiogram.client.default import DefaultBotProperties
from aiogram.filters import CommandStart

# Получение токена безопасно
BOT_TOKEN = os.getenv("BOT_TOKEN")

bot = Bot(
    token=BOT_TOKEN,
    default=DefaultBotProperties(parse_mode=ParseMode.HTML)
)
dp = Dispatcher()

@dp.message(CommandStart())
async def start(message: Message):
    keyboard = ReplyKeyboardMarkup(
        keyboard=[[
            KeyboardButton(
                text="🧮 Открыть калькулятор плитки",
                web_app=WebAppInfo(url="https://andrei-web-star.github.io/calc_tile_webapp/")
            )
        ]],
        resize_keyboard=True
    )
    await message.answer(
        "Привет! 👋 Я — Калькулятор плитки от <b>ДИЗ БАЛАНС</b>.\n\n"
        "Нажми кнопку ниже, чтобы открыть Mini App:",
        reply_markup=keyboard
    )

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())