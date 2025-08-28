import logging
from aiogram import Bot, Dispatcher, types
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo, ReplyKeyboardMarkup, KeyboardButton
from aiogram.enums import ParseMode
from aiogram.filters import Command
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram import F

import asyncio

# Замените на свой токен
TOKEN = "ВАШ_НОВЫЙ_ТОКЕН"

# Инициализация бота и диспетчера
bot = Bot(token=TOKEN, parse_mode=ParseMode.HTML)
dp = Dispatcher(storage=MemoryStorage())

# Состояния FSM
class TileTypeState(StatesGroup):
    choosing_tile_type = State()

# Команда /start
@dp.message(Command("start"))
async def cmd_start(message: Message, state: FSMContext):
    await state.clear()

    # Кнопка на Mini App ColorMood
    colormood_button = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="🎨 Открыть ColorMood Pro",
                    web_app=WebAppInfo(url="https://colormood.vercel.app")
                )
            ]
        ]
    )

    # Покажем кнопку на Mini App сразу
    await message.answer("🎨 <b>ColorMood Pro</b> — генератор палитр и мудбордов от ДИЗ БАЛАНС:\n👇 Нажми, чтобы открыть:", reply_markup=colormood_button)

    # Затем — калькулятор плитки
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="🧱 Настенная"), KeyboardButton(text="🧱 Напольная")]
        ],
        resize_keyboard=True
    )

    await message.answer(
        "Привет! Я — Калькулятор плитки от <b>ДИЗ БАЛАНС</b>. 🧱\n"
        "Я помогу рассчитать нужное количество <b>настенной</b> или <b>напольной</b> плитки с учётом размеров, швов, раскладки и запаса.\n\n"
        "<b>Все значения вводи в метрах</b>, а размеры плитки — в <b>миллиметрах</b>.\n"
        "Если число не целое — можно с запятой или точкой (например: 2,5 или 2.5).\n\n"
        "Выбери тип плитки:",
        reply_markup=keyboard
    )

    await state.set_state(TileTypeState.choosing_tile_type)

# Обработка выбора плитки
@dp.message(TileTypeState.choosing_tile_type)
async def choose_tile_type(message: Message, state: FSMContext):
    if message.text == "🧱 Настенная":
        await message.answer("🔧 Введи параметры для настенной плитки:")
    elif message.text == "🧱 Напольная":
        await message.answer("🔧 Введи параметры для напольной плитки:")
    else:
        await message.answer("Выбери вариант с клавиатуры 👇")

# Запуск бота
async def main():
    logging.basicConfig(level=logging.INFO)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
