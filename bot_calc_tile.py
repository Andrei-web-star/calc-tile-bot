import asyncio
import logging
from aiogram import Bot, Dispatcher, F
from aiogram.types import Message
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
import os

# === НАСТРОЙКИ ===
API_TOKEN = os.getenv("BOT_TOKEN")

# Логирование (полезно на Render)
logging.basicConfig(level=logging.INFO)
log = logging.getLogger("tile-bot")

bot = Bot(
    token=API_TOKEN,
    default=DefaultBotProperties(parse_mode=ParseMode.HTML)
)
dp = Dispatcher()

# Списки допустимых вариантов
TYPE_WALL = "🧱 Настенная"
TYPE_FLOOR = "🧱 Напольная"
LAYOUTS = ["прямая раскладка", "со смещением", "по диагонали", "нет"]

# Состояния
class TileStates(StatesGroup):
    type = State()
    length = State()
    width = State()
    height = State()
    door_width = State()
    door_height = State()
    bath_length = State()
    bath_width = State()
    bath_height = State()
    has_screen = State()
    tile_length = State()
    tile_width = State()
    tile_price = State()
    seam = State()
    layout = State()
    reserve = State()

# Утилки
def parse_float(value: str) -> float | None:
    """Поддержка запятой/точки и трим пробелов"""
    if not value or not value.strip():
        return None
    try:
        return float(value.strip().replace(",", "."))
    except ValueError:
        return None

def must_be_positive(x: float, allow_zero: bool = False) -> bool:
    return (x is not None) and (x >= 0 if allow_zero else x > 0)

def kb(rows: list[list[str]]) -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text=t) for t in row] for row in rows],
        resize_keyboard=True
    )

# Команды
@dp.message(F.text.in_({"/start", "🔁 Посчитать заново"}))
async def start(message: Message, state: FSMContext):
    await state.clear()
    await message.answer(
        "Привет! Я — Калькулятор плитки от ДИЗ БАЛАНС. 🧱\n"
        "Я помогу рассчитать нужное количество <b>настенной</b> или <b>напольной</b> плитки "
        "с учётом размеров, швов, раскладки и запаса.\n\n"
        "Все значения вводи в <b>метрах</b>, а размеры плитки — в <b>миллиметрах</b>.\n"
        "Если число не целое — можно с запятой или точкой (например: 2,5 или 2.5).\n\n"
        "Выбери тип плитки:",
        reply_markup=kb([[TYPE_WALL], [TYPE_FLOOR]])
    )
    await state.set_state(TileStates.type)

# Тип
@dp.message(TileStates.type)
async def get_type(message: Message, state: FSMContext):
    if message.text not in (TYPE_WALL, TYPE_FLOOR):
        await message.answer("Выбери вариант на клавиатуре 👇", reply_markup=kb([[TYPE_WALL], [TYPE_FLOOR]]))
        return
    await state.update_data(type=message.text)
    await message.answer("Укажи длину помещения (м):")
    await state.set_state(TileStates.length)

# Длина
@dp.message(TileStates.length)
async def get_length(message: Message, state: FSMContext):
    val = parse_float(message.text)
    if not must_be_positive(val):
        await message.answer("❌ Введи положительное число, например: 2.5")
        return
    await state.update_data(length=val)
    await message.answer("Укажи ширину помещения (м):")
    await state.set_state(TileStates.width)

# Ширина
@dp.message(TileStates.width)
async def get_width(message: Message, state: FSMContext):
    val = parse_float(message.text)
    if not must_be_positive(val):
        await message.answer("❌ Введи положительное число, например: 1.8")
        return
    await state.update_data(width=val)
    data = await state.get_data()
    if data["type"] == TYPE_WALL:
        await message.answer("Укажи высоту помещения (м):")
        await state.set_state(TileStates.height)
    else:
        await message.answer("Укажи длину плитки (мм):")
        await state.set_state(TileStates.tile_length)

# Высота (только для стен)
@dp.message(TileStates.height)
async def get_height(message: Message, state: FSMContext):
    val = parse_float(message.text)
    if not must_be_positive(val):
        await message.answer("❌ Введи положительное число, например: 2.5")
        return
    await state.update_data(height=val)
    await message.answer("Укажи ширину двери (м):")
    await state.set_state(TileStates.door_width)

@dp.message(TileStates.door_width)
async def get_door_width(message: Message, state: FSMContext):
    val = parse_float(message.text)
    if not must_be_positive(val, allow_zero=True):
        await message.answer("❌ Введи число ≥ 0, например: 0.7 (можно 0)")
        return
    await state.update_data(door_width=val)
    await message.answer("Укажи высоту двери (м):")
    await state.set_state(TileStates.door_height)

@dp.message(TileStates.door_height)
async def get_door_height(message: Message, state: FSMContext):
    val = parse_float(message.text)
    if not must_be_positive(val, allow_zero=True):
        await message.answer("❌ Введи число ≥ 0, например: 2 (можно 0)")
        return
    await state.update_data(door_height=val)
    await message.answer("Укажи длину ванны (м):")
    await state.set_state(TileStates.bath_length)

@dp.message(TileStates.bath_length)
async def get_bath_length(message: Message, state: FSMContext):
    val = parse_float(message.text)
    if not must_be_positive(val, allow_zero=True):
        await message.answer("❌ Введи число ≥ 0, например: 1.7 (можно 0)")
        return
    await state.update_data(bath_length=val)
    await message.answer("Укажи ширину ванны (м):")
    await state.set_state(TileStates.bath_width)

@dp.message(TileStates.bath_width)
async def get_bath_width(message: Message, state: FSMContext):
    val = parse_float(message.text)
    if not must_be_positive(val, allow_zero=True):
        await message.answer("❌ Введи число ≥ 0, например: 0.75 (можно 0)")
        return
    await state.update_data(bath_width=val)
    await message.answer("Укажи высоту ванны (м):")
    await state.set_state(TileStates.bath_height)

@dp.message(TileStates.bath_height)
async def get_bath_height(message: Message, state: FSMContext):
    val = parse_float(message.text)
    if not must_be_positive(val, allow_zero=True):
        await message.answer("❌ Введи число ≥ 0, например: 0.45 (можно 0)")
        return
    await state.update_data(bath_height=val)
    await message.answer("Нужно ли укладывать экран под ванну? (да/нет)")
    await state.set_state(TileStates.has_screen)

@dp.message(TileStates.has_screen)
async def get_screen(message: Message, state: FSMContext):
    ans = message.text.strip().lower()
    if ans not in ("да", "нет"):
        await message.answer("Ответь «да» или «нет».")
        return
    await state.update_data(has_screen=(ans == "да"))
    await message.answer("Укажи длину плитки (мм):")
    await state.set_state(TileStates.tile_length)

# Размер плитки, цена, шов — общие
@dp.message(TileStates.tile_length)
async def get_tile_length(message: Message, state: FSMContext):
    val = parse_float(message.text)
    if not must_be_positive(val):
        await message.answer("❌ Введи положительное число, например: 600")
        return
    await state.update_data(tile_length=val / 1000)  # в метры
    await message.answer("Укажи ширину плитки (мм):")
    await state.set_state(TileStates.tile_width)

@dp.message(TileStates.tile_width)
async def get_tile_width(message: Message, state: FSMContext):
    val = parse_float(message.text)
    if not must_be_positive(val):
        await message.answer("❌ Введи положительное число, например: 300")
        return
    await state.update_data(tile_width=val / 1000)
    await message.answer("Укажи цену плитки за 1 м² (руб):")
    await state.set_state(TileStates.tile_price)

@dp.message(TileStates.tile_price)
async def get_tile_price(message: Message, state: FSMContext):
    val = parse_float(message.text)
    if not must_be_positive(val):
        await message.answer("❌ Введи положительное число, например: 1200")
        return
    await state.update_data(tile_price=val)
    await message.answer("Укажи ширину шва (мм):")
    await state.set_state(TileStates.seam)

@dp.message(TileStates.seam)
async def get_seam(message: Message, state: FSMContext):
    val = parse_float(message.text)
    if val is None or val < 0:
        await message.answer("❌ Введи число ≥ 0, например: 1.5")
        return
    await state.update_data(seam=val / 1000)
    await message.answer(
        "Выбери тип раскладки:",
        reply_markup=kb([["прямая раскладка"], ["со смещением"], ["по диагонали"], ["нет"]])
    )
    await state.set_state(TileStates.layout)

@dp.message(TileStates.layout)
async def get_layout(message: Message, state: FSMContext):
    layout = message.text.lower()
    if layout not in LAYOUTS:
        await message.answer("Выбери вариант на клавиатуре 👇",
                             reply_markup=kb([["прямая раскладка"], ["со смещением"], ["по диагонали"], 
["нет"]]))
        return
    await state.update_data(layout=layout)
    await message.answer("Укажи процент запаса (например: 5):")
    await state.set_state(TileStates.reserve)

@dp.message(TileStates.reserve)
async def calculate(message: Message, state: FSMContext):
    val = parse_float(message.text)
    if val is None or val < 0:
        await message.answer("❌ Введи число ≥ 0, например: 5")
        return
    await state.update_data(reserve=val)

    data = await state.get_data()
    try:
        # 1) Базовая площадь
        if data["type"] == TYPE_WALL:
            perimeter = 2 * (data["length"] + data["width"])
            wall_area = perimeter * data["height"]
            door_area = max(0.0, data["door_width"] * data["door_height"])
            bath_area = max(0.0, data["bath_length"] * data["bath_height"])
            screen_area = max(0.0, data["bath_width"] * data["bath_height"]) if data["has_screen"] else 0.0
            base_area = wall_area - door_area - bath_area + screen_area
        else:
            base_area = data["length"] * data["width"]
            door_area = bath_area = screen_area = 0.0

        if base_area <= 0:
            await message.answer("❗️Площадь получилась ≤ 0. Проверь параметры и начни заново: /start")
            await state.clear()
            return

        # 2) Надбавка по раскладке
        layout = data["layout"]
        if layout == "со смещением":
            base_area *= 1.05
        elif layout == "по диагонали":
            base_area *= 1.10

        # 3) Запас
        total_area = base_area * (1 + data["reserve"] / 100)

        # 4) Кол-во плиток и стоимость
        tile_area = data["tile_length"] * data["tile_width"]
        if tile_area <= 0:
            await message.answer("❗️Неверные размеры плитки. Начни заново: /start")
            await state.clear()
            return

        tile_count = total_area / tile_area
        cost = total_area * data["tile_price"]

        await message.answer(
            f"<b>📊 Результаты расчёта:</b>\n\n"
            f"▪️ Площадь укладки: <b>{total_area:.2f} м²</b>\n"
            f"▪️ Стоимость: <b>{cost:.0f} руб</b>\n"
            f"▪️ Кол-во плитки: <b>{tile_count:.0f} шт</b>\n"
            f"▪️ Площадь двери: {door_area:.2f} м²\n"
            f"▪️ Площадь ванны: {bath_area:.2f} м²\n"
            f"▪️ Площадь экрана: {screen_area:.2f} м²\n"
            f"▪️ Раскладка: {layout}\n\n"
            f"🔁 <b>Посчитать заново</b> — нажми /start"
        )
    except Exception as e:
        log.exception("calc failed: %s", e)
        await message.answer("❌ Неожиданная ошибка при расчёте. Попробуй ещё раз: /start")
    finally:
        await state.clear()

# Базовый обработчик «вне сценария» — чтобы бот не молчал
@dp.message()
async def fallback(message: Message):
    await message.answer("Я жду ответ на текущий вопрос. Чтобы начать заново — /start")

# Запуск (для Render/локально)
async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
