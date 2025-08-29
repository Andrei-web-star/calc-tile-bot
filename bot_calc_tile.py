import os
from aiogram import Bot, Dispatcher, F
from aiogram.enums import ParseMode
from aiogram.types import Message, WebAppInfo, ReplyKeyboardMarkup, KeyboardButton
from aiogram.client.default import DefaultBotProperties
from aiogram.filters import CommandStart
from aiogram.types import ReplyKeyboardRemove

from aiogram import Router
from aiogram import types

import asyncio

# Получение токена из переменной окружения
BOT_TOKEN = os.getenv("BOT_TOKEN")

# Инициализация бота с правильным способом задания parse_mode
bot = Bot(
    token=BOT_TOKEN,
    default=DefaultBotProperties(parse_mode=ParseMode.HTML)
)

# Диспетчер
dp = Dispatcher()

# Роутер (если нужно, можно расширять)
router = Router()
dp.include_router(router)


# Обработка /start с кнопкой WebApp
@dp.message(CommandStart())
async def start(message: Message):
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Открыть калькулятор плитки 🧮", web_app=WebAppInfo(url="https://calc-tile-bot.onrender.com"))]
        ],
        resize_keyboard=True
    )

    await message.answer(
        "Привет! 👋\nЯ — Калькулятор плитки от <b>ДИЗ БАЛАНС</b>.\n\nНажми кнопку ниже, чтобы перейти в Mini App:",
        reply_markup=keyboard
    )


# На случай если нужно выключить клавиатуру
@dp.message(F.text.lower() == "удалить клавиатуру")
async def remove_keyboard(message: Message):
    await message.answer("Клавиатура удалена", reply_markup=ReplyKeyboardRemove())


# Запуск
async def main():
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
