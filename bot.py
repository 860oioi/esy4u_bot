# Добавьте эти импорты в начало файла
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton


# Обработчик команды /progress
@router.message(Command("progress"))
async def cmd_progress(message: Message):
    user_data = await db.get_user_data(message.from_user.id)

    if not user_data:
        await message.answer("Сначала пройди онбординг через /start")
        return

    # Здесь будет расчет прогресса (заглушка)
    days_without = 7  # Замените на реальный расчет
    money_saved = 1500  # Замените на реальный расчет

    await message.answer(f"📊 Твой прогресс:\n"
                         f"Дней без курения: {days_without}\n"
                         f"Сэкономлено: {money_saved} ₽\n"
                         f"Ты молодец! 💪")


# Обработчик команды /tianet
@router.message(Command("tianet"))
async def cmd_tianet(message: Message):
    # Случайная мотивационная фраза
    motivations = [
        "Дыши глубже 5 раз. Тяга пройдет через 5 минут!",
        "Вспомни, зачем ты начал(а). Ты сильнее этой привычки!",
        "Выпей стакан воды. Ты управляешь собой, а не никотин тобой!",
        "Сделай 10 приседаний. Отвлеки тело, ум последует за ним!"
    ]

    import random
    motivation = random.choice(motivations)

    await message.answer(f"💪 {motivation}")


# Обработчик команды /myinfo
@router.message(Command("myinfo"))
async def cmd_myinfo(message: Message):
    user_data = await db.get_user_data(message.from_user.id)

    if not user_data:
        await message.answer("Сначала пройди онбординг через /start")
        return

    device_names = {
        "cigarettes": "🚬 Сигареты",
        "disposable_vape": "💨 Одноразка",
        "vape": "🔋 Вейп",
        "none": "❌ Уже не курю"
    }

    response = (
        "📋 Твои данные:\n"
        f"Причина: {user_data.get('reason_to_quit', 'Не указана')}\n"
        f"Устройство: {device_names.get(user_data.get('device_type'), 'Не указано')}\n"
        f"Дата начала: {user_data.get('start_date', 'Не указана')}")

    await message.answer(response)


# Обработчик команды /help
@router.message(Command("help"))
async def cmd_help(message: Message):
    help_text = ("🤖 Помощь по боту:\n\n"
                 "/start - Начать работу\n"
                 "/progress - Статистика прогресса\n"
                 "/tianet - Помощь когда тянет курить\n"
                 "/myinfo - Мои данные\n"
                 "/support - Связь с разработчиком\n\n"
                 "Бот будет присылать ежедневные мотивационные сообщения!")
    await message.answer(help_text)


# Обработчик команды /support
@router.message(Command("support"))
async def cmd_support(message: Message):
    await message.answer("📧 По вопросам и предложениям:\n"
                         "Напиши разработчику: @твой_юзернейм\n\n"
                         "Расскажи, что можно улучшить в боте!")


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
    await message.answer("Привет 👋\n"
                         "Я помогу тебе бросить курить 💪\n\n"
                         "Почему ты хочешь бросить?\n"
                         "(Можно коротко: ради семьи, здоровья, денег и т.д.)")


# --- Обработка ответа 'почему' ---
@dp.message()
async def handle_message(message: types.Message):
    user_id = message.from_user.id
    text = message.text.lower().strip()

    # если пользователь отвечает "не знаю"
    if any(phrase in text for phrase in
           ["не знаю", "незнаю", "хз", "фиг", "не уверен", "просто так"]):
        await message.answer(
            "А может тогда тебе и не надо бросать, раз всё нравится? 😏")
        await asyncio.sleep(2)
        await message.answer("Так всё-таки, зачем тебе бросать?")
        return

    # сохраняем причину
    user_data[user_id]["reason"] = message.text
    await message.answer(
        f"Отлично 👍\nЗапомнил: ты хочешь бросить, потому что {message.text} 💪")

    # следующий шаг — уточняем, что человек курит
    await asyncio.sleep(1)
    await message.answer(
        "Теперь скажи, что именно ты куришь?\n1️⃣ Сигареты\n2️⃣ HQD / Elfbar / одноразки"
    )


# --- Запуск ---
async def main():
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
