import asyncio
import logging
from aiogram import Bot, Dispatcher, Router, F
from aiogram.types import Message, ReplyKeyboardRemove
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext

from config import BOT_TOKEN
from states import UserState
from database import Database

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Инициализация бота и диспетчера
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()
router = Router()  # ⬅️ ЭТУ СТРОКУ НУЖНО ДОБАВИТЬ ПЕРЕД ВСЕМИ ОБРАБОТЧИКАМИ
dp.include_router(router)

# Инициализация базы данных
db = Database()

# Списки триггерных фраз для "не знаю"
UNKNOWN_PHRASES = ["не знаю", "незнаю", "хз", "фиг", "не уверен", "просто так", "надоело", "потому что все", "за company"]

# ==================== ОБРАБОТЧИКИ КОМАНД ====================

@router.message(Command("start"))
async def cmd_start(message: Message, state: FSMContext):
    await message.answer(
        "Привет! Я помогу тебе бросить курить — без морали, с юмором и по уму.\n"
        "Хочешь начать свой путь к свободе?",
        reply_markup=create_simple_keyboard(["Да, поехали!"])
    )
    await state.set_state(UserState.waiting_for_reason)

@router.message(Command("progress"))
async def cmd_progress(message: Message):
    user_data = await db.get_user_data(message.from_user.id)
    
    if not user_data:
        await message.answer("Сначала пройди онбординг через /start")
        return
    
    # Здесь будет расчет прогресса (заглушка)
    days_without = 7  # Замените на реальный расчет
    money_saved = 1500  # Замените на реальный расчет
    
    await message.answer(
        f"📊 Твой прогресс:\n"
        f"Дней без курения: {days_without}\n"
        f"Сэкономлено: {money_saved} ₽\n"
        f"Ты молодец! 💪"
    )

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
        f"Дата начала: {user_data.get('start_date', 'Не указана')}"
    )
    
    await message.answer(response)

@router.message(Command("help"))
async def cmd_help(message: Message):
    help_text = (
        "🤖 Помощь по боту:\n\n"
        "/start - Начать работу\n"
        "/progress - Статистика прогресса\n"
        "/tianet - Помощь когда тянет курить\n"
        "/myinfo - Мои данные\n"
        "/support - Связь с разработчиком\n\n"
        "Бот будет присылать ежедневные мотивационные сообщения!"
    )
    await message.answer(help_text)

@router.message(Command("support"))
async def cmd_support(message: Message):
    await message.answer(
        "📧 По вопросам и предложениям:\n"
        "Напиши разработчику: @твой_юзернейм\n\n"
        "Расскажи, что можно улучшить в боте!"
    )

# ==================== ОНБОРДИНГ (ваш старый код) ====================

@router.message(UserState.waiting_for_reason, F.text == "Да, поехали!")
async def ask_reason(message: Message, state: FSMContext):
    await message.answer(
        "Почему ты хочешь бросить курить?\n"
        "(Можно коротко: ради семьи, здоровья, денег, спорта — что угодно)",
        reply_markup=ReplyKeyboardRemove()
    )

@router.message(UserState.waiting_for_reason)
async def process_reason(message: Message, state: FSMContext):
    user_answer = message.text.lower().strip()
    
    # Проверяем, является ли ответ "не знаю"
    if any(phrase in user_answer for phrase in UNKNOWN_PHRASES):
        await message.answer("А может тогда тебе и не надо бросать, раз всё нравится? 😏")
        await asyncio.sleep(2)
        await message.answer("Так всё-таки, зачем тебе бросать?\nДумай честно — не для меня, а для себя.")
        return
    
    # Сохраняем причину и переходим к следующему шагу
    await state.update_data(reason_to_quit=message.text)
    await ask_device_type(message, state)

async def ask_device_type(message: Message, state: FSMContext):
    await message.answer(
        "Что ты обычно куришь?",
        reply_markup=create_simple_keyboard(["🚬 Сигареты", "💨 Одноразка (HQD/Elf Bar)", "🔋 Вейп", "❌ Уже не курю"])
    )
    await state.set_state(UserState.waiting_for_device_type)

# ... (остальной код онбординга оставьте без изменений)

# ==================== ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ ====================

def create_simple_keyboard(buttons):
    from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
    keyboard = [[KeyboardButton(text=button)] for button in buttons]
    return ReplyKeyboardMarkup(keyboard=keyboard, resize_keyboard=True)

async def main():
    # Создаем таблицу при запуске
    await db.create_table()
    
    # Запускаем бота
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
