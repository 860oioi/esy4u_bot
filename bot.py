import asyncio
import logging
import os
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from dotenv import load_dotenv

# Загружаем токен
load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")

# Логирование
logging.basicConfig(level=logging.INFO)

# Инициализация бота
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# Храним состояние пользователей (в памяти, потом заменим на БД)
user_data = {}

# --- Команда /start ---
@dp.message(Command("start"))
async def start_handler(message: types.Message):
    user_data[message.from_user.id] = {}
    await message.answer(
        "Привет 👋\n"
        "Я помогу тебе бросить курить 💪\n\n"
        "Почему ты хочешь бросить?\n"
        "(Можно коротко: ради семьи, здоровья, денег и т.д.)"
    )

# --- Обработка ответа 'почему' ---
@dp.message()
async def handle_message(message: types.Message):
    user_id = message.from_user.id
    text = message.text.lower().strip()

    # если пользователь отвечает "не знаю"
    if any(phrase in text for phrase in ["не знаю", "незнаю", "хз", "фиг", "не уверен", "просто так"]):
        await message.answer("А может тогда тебе и не надо бросать, раз всё нравится? 😏")
        await asyncio.sleep(2)
        await message.answer("Так всё-таки, зачем тебе бросать?")
        return

    # сохраняем причину
    user_data[user_id]["reason"] = message.text
    await message.answer(f"Отлично 👍\nЗапомнил: ты хочешь бросить, потому что {message.text} 💪")

    # следующий шаг — уточняем, что человек курит
    await asyncio.sleep(1)
    await message.answer("Теперь скажи, что именно ты куришь?\n1️⃣ Сигареты\n2️⃣ HQD / Elfbar / одноразки")

# --- Запуск ---
async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
