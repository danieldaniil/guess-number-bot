import asyncio
import random
import logging
from aiogram import Bot, Dispatcher, F
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton
from aiogram.filters import Command

# Настройка логирования
logging.basicConfig(level=logging.INFO)

# ⚠️ ВСТАВЬ СВОЙ ТОКЕН ЗДЕСЬ! ⚠️
TOKEN = "8377511577:AAE_DQ8AYjK5cZLDgGEWt0r-Gwfpb1-HP_U"  # ЗАМЕНИ на свой токен!

bot = Bot(token=TOKEN)
dp = Dispatcher()

# Храним данные игроков
games = {}
user_stats = {}
previous_guesses = {}
user_language = {}  # Храним язык пользователей

# --- Тексты на разных языках ---
TEXTS = {
    "ru": {
        "start": "🎮 Добро пожаловать в игру 'Угадай число'!\n\nВыбери режим игры:",
        "main_menu": [
            ["🎯 Я загадаю число"],
            ["🤖 Бот загадает число"],
            ["📊 Статус", "❓ Помощь"],
            ["🌐 Язык / Language"]
        ],
        "back": "🔙 Назад",
        "ready": "✅ Готов",
        "give_up": "🏳️ Сдаться",
        "send": "Отправить ✅",
        "delete": "⌫ Назад",
        "game_buttons": ["➕ Больше", "➖ Меньше", "🎉 Угадал"],
        "help": """🎮 <b>Правила игры:</b>

<b>Режим 1: 🤖 Бот загадывает число</b>
• Я загадываю число от 1 до 100
• Ты вводишь свои варианты
• Я подсказываю 'больше' или 'меньше'
• 🏳️ Можно сдаться в любой момент

<b>Режим 2: 🎯 Ты загадываешь число</b>
• Ты загадываешь число от 1 до 100
• Я пытаюсь угадать его
• Ты отвечаешь 'больше', 'меньше' или 'угадал'

📊 Используй кнопку <b>Статус</b> для статистики
🗑️ Очисти чат чтобы сбросить статистику""",
        "bot_thinking": "🤖 Я загадал число от 1 до 100!\n\n🔢 Вводи цифры с клавиатуры\n🏳️ Можешь сдаться в любой момент",
        "current_number": "📋 Текущее число: {}",
        "enter_number": "❌ Введите число!",
        "number_range": "❌ Число должно быть от 1 до 100!",
        "higher": "📈 Моё число больше!\n🔢 Твои числа: {}",
        "lower": "📉 Моё число меньше!\n🔢 Твои числа: {}",
        "win": "🎉 Поздравляю! Ты угадал число {}!\n🏆 Попыток: {}",
        "give_up_msg": """🏳️ Ты сдался!

🔢 Загаданное число было: {}
🎯 Ты сделал попыток: {}

💪 Не расстраивайся! Попробуй ещё раз!
✨ Подсказка: используй стратегию половинного деления""",
        "user_thinking": "🎯 Загадай число от 1 до 100!",
        "bot_guess": "🤔 Мой вариант: {}",
        "bot_win": "🎉 Ура! Я угадал твое число {} за {} попыток!",
        "no_active_game": "Сейчас нет активной игры для сдачи!",
        "stats_none": "📊 <b>Статистика отсутствует</b>\n\nТы еще не сыграл ни одной игры!\n🎯 Выбери режим игры и начни прямо сейчас!",
        "use_keyboard": "🔢 Используй цифровую клавиатуру",
        "use_buttons": "🎯 Используй кнопки для ответа",
        "choose_mode": "🎮 Выбери режим игры:",
        "language_changed": "🌐 Язык изменен на Русский",
        "choose_language": "Выбери язык / Choose language:"
    },
    "en": {
        "start": "🎮 Welcome to 'Guess the Number' game!\n\nChoose game mode:",
        "main_menu": [
            ["🎯 I'll think of a number"],
            ["🤖 Bot will think of a number"],
            ["📊 Stats", "❓ Help"],
            ["🌐 Language / Язык"]
        ],
        "back": "🔙 Back",
        "ready": "✅ Ready",
        "give_up": "🏳️ Give up",
        "send": "Send ✅",
        "delete": "⌫ Delete",
        "game_buttons": ["➕ Higher", "➖ Lower", "🎉 Guessed"],
        "help": """🎮 <b>Game Rules:</b>

<b>Mode 1: 🤖 Bot thinks of a number</b>
• I think of a number from 1 to 100
• You enter your guesses
• I tell 'higher' or 'lower'
• 🏳️ You can give up anytime

<b>Mode 2: 🎯 You think of a number</b>
• You think of a number from 1 to 100
• I try to guess it
• You answer 'higher', 'lower' or 'guessed'

📊 Use <b>Stats</b> button for statistics
🗑️ Clear chat to reset statistics""",
        "bot_thinking": "🤖 I thought of a number from 1 to 100!\n\n🔢 Enter numbers using keyboard\n🏳️ You can give up anytime",
        "current_number": "📋 Current number: {}",
        "enter_number": "❌ Please enter a number!",
        "number_range": "❌ Number must be from 1 to 100!",
        "higher": "📈 My number is higher!\n🔢 Your numbers: {}",
        "lower": "📉 My number is lower!\n🔢 Your numbers: {}",
        "win": "🎉 Congratulations! You guessed the number {}!\n🏆 Attempts: {}",
        "give_up_msg": """🏳️ You gave up!

🔢 The secret number was: {}
🎯 You made attempts: {}

💪 Don't worry! Try again!
✨ Tip: use the half-division strategy""",
        "user_thinking": "🎯 Think of a number from 1 to 100!",
        "bot_guess": "🤔 My guess: {}",
        "bot_win": "🎉 Hooray! I guessed your number {} in {} attempts!",
        "no_active_game": "No active game to give up!",
        "stats_none": "📊 <b>No statistics yet</b>\n\nYou haven't played any games yet!\n🎯 Choose game mode and start now!",
        "use_keyboard": "🔢 Use the number keyboard",
        "use_buttons": "🎯 Use buttons to answer",
        "choose_mode": "🎮 Choose game mode:",
        "language_changed": "🌐 Language changed to English",
        "choose_language": "Choose language / Выбери язык:"
    }
}

# --- Функции для получения текста ---
def get_text(user_id, key, *args):
    lang = user_language.get(user_id, "ru")
    text = TEXTS[lang][key]
    if args:
        return text.format(*args)
    return text

def get_main_menu(user_id):
    lang = user_language.get(user_id, "ru")
    buttons = []
    for row in TEXTS[lang]["main_menu"]:
        button_row = [KeyboardButton(text=text) for text in row]
        buttons.append(button_row)
    return ReplyKeyboardMarkup(keyboard=buttons, resize_keyboard=True)

def get_number_pad(user_id):
    lang = user_language.get(user_id, "ru")
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="1"), KeyboardButton(text="2"), KeyboardButton(text="3")],
            [KeyboardButton(text="4"), KeyboardButton(text="5"), KeyboardButton(text="6")],
            [KeyboardButton(text="7"), KeyboardButton(text="8"), KeyboardButton(text="9")],
            [KeyboardButton(text="0"), KeyboardButton(text=get_text(user_id, "delete"))],
            [KeyboardButton(text=get_text(user_id, "send")), KeyboardButton(text=get_text(user_id, "give_up"))]
        ],
        resize_keyboard=True
    )

def get_ready_kb(user_id):
    lang = user_language.get(user_id, "ru")
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text=get_text(user_id, "ready"))],
            [KeyboardButton(text=get_text(user_id, "back"))]
        ],
        resize_keyboard=True
    )

def get_game_kb(user_id):
    lang = user_language.get(user_id, "ru")
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text=get_text(user_id, "game_buttons")[0]), KeyboardButton(text=get_text(user_id, "game_buttons")[1])],
            [KeyboardButton(text=get_text(user_id, "game_buttons")[2]), KeyboardButton(text=get_text(user_id, "back"))]
        ],
        resize_keyboard=True
    )

def get_language_kb():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="🇷🇺 Русский"), KeyboardButton(text="🇺🇸 English")],
            [KeyboardButton(text="🔙 Назад / Back")]
        ],
        resize_keyboard=True
    )

# --- Основные команды ---
@dp.message(Command("start"))
async def cmd_start(message: Message):
    user_id = message.from_user.id
    
    # Устанавливаем язык по умолчанию
    if user_id not in user_language:
        user_language[user_id] = "ru"
    
    # Очищаем данные
    if user_id in games:
        del games[user_id]
    if user_id in previous_guesses:
        del previous_guesses[user_id]
    
    await message.answer(get_text(user_id, "start"), reply_markup=get_main_menu(user_id))

@dp.message(F.text == "🔙 Назад")
@dp.message(F.text == "🔙 Back")
async def go_back(message: Message):
    user_id = message.from_user.id
    if user_id in games:
        del games[user_id]
    await message.answer(get_text(user_id, "choose_mode"), reply_markup=get_main_menu(user_id))

@dp.message(F.text == "🌐 Язык / Language")
@dp.message(F.text == "🌐 Language / Язык")
async def change_language(message: Message):
    user_id = message.from_user.id
    await message.answer(get_text(user_id, "choose_language"), reply_markup=get_language_kb())

@dp.message(F.text == "🇷🇺 Русский")
async def set_russian(message: Message):
    user_id = message.from_user.id
    user_language[user_id] = "ru"
    await message.answer(get_text(user_id, "language_changed"), reply_markup=get_main_menu(user_id))

@dp.message(F.text == "🇺🇸 English")
async def set_english(message: Message):
    user_id = message.from_user.id
    user_language[user_id] = "en"
    await message.answer("🌐 Language changed to English", reply_markup=get_main_menu(user_id))

# --- Кнопка Сдаться ---
@dp.message(F.text == "🏳️ Сдаться")
@dp.message(F.text == "🏳️ Give up")
async def give_up(message: Message):
    user_id = message.from_user.id
    
    if user_id in games and games[user_id]["mode"] == "bot_thinks":
        number = games[user_id]["number"]
        attempts = games[user_id]["attempts"]
        
        # Добавляем поражение в статистику
        if user_id not in user_stats:
            user_stats[user_id] = {"wins": 0, "attempts": 0, "losses": 0}
        user_stats[user_id]["losses"] += 1
        user_stats[user_id]["attempts"] += attempts
        
        await message.answer(
            get_text(user_id, "give_up_msg", number, attempts),
            reply_markup=get_main_menu(user_id)
        )
        
        # Очищаем данные игры
        del games[user_id]
        if user_id in previous_guesses:
            del previous_guesses[user_id]
            
    else:
        await message.answer(get_text(user_id, "no_active_game"), reply_markup=get_main_menu(user_id))

# --- Помощь ---
@dp.message(F.text == "❓ Помощь")
@dp.message(F.text == "❓ Help")
async def cmd_help(message: Message):
    user_id = message.from_user.id
    await message.answer(get_text(user_id, "help"), parse_mode="HTML")

# --- Статус и статистика ---
@dp.message(F.text == "📊 Статус")
@dp.message(F.text == "📊 Stats")
@dp.message(Command("stats"))
async def cmd_stats(message: Message):
    user_id = message.from_user.id
    
    if user_id in user_stats:
        stats = user_stats[user_id]
        wins = stats['wins']
        losses = stats.get('losses', 0)
        total_attempts = stats['attempts']
        total_games = wins + losses
        
        if wins > 0:
            avg_attempts = total_attempts // wins
            success_rate = (wins / total_games) * 100 if total_games > 0 else 0
        else:
            avg_attempts = 0
            success_rate = 0
        
        if user_language.get(user_id, "ru") == "ru":
            status_text = (
                f"📊 <b>Твой статус:</b>\n\n"
                f"🏆 Побед: {wins}\n"
                f"🏳️ Поражений: {losses}\n"
                f"🎯 Всего попыток: {total_attempts}\n"
                f"📈 Среднее за игру: {avg_attempts} попыток\n"
                f"💯 Процент успеха: {success_rate:.1f}%\n\n"
            )
        else:
            status_text = (
                f"📊 <b>Your stats:</b>\n\n"
                f"🏆 Wins: {wins}\n"
                f"🏳️ Losses: {losses}\n"
                f"🎯 Total attempts: {total_attempts}\n"
                f"📈 Average per game: {avg_attempts} attempts\n"
                f"💯 Success rate: {success_rate:.1f}%\n\n"
            )
        
        await message.answer(status_text, parse_mode="HTML")
        
    else:
        await message.answer(get_text(user_id, "stats_none"), parse_mode="HTML")

# --- Бот загадывает число ---
@dp.message(F.text == "🤖 Бот загадает число")
@dp.message(F.text == "🤖 Bot will think of a number")
async def bot_thinks_mode(message: Message):
    user_id = message.from_user.id
    games[user_id] = {
        "mode": "bot_thinks", 
        "number": random.randint(1, 100), 
        "input": "",
        "attempts": 0
    }
    previous_guesses[user_id] = []
    await message.answer(get_text(user_id, "bot_thinking"), reply_markup=get_number_pad(user_id))

@dp.message(F.text.in_(list("0123456789")))
async def user_input_number(message: Message):
    user_id = message.from_user.id
    if user_id in games and games[user_id]["mode"] == "bot_thinks":
        if len(games[user_id]["input"]) < 3:
            games[user_id]["input"] += message.text
            await message.answer(
                get_text(user_id, "current_number", games[user_id]['input']), 
                reply_markup=get_number_pad(user_id)
            )

@dp.message(F.text == "⌫ Назад")
@dp.message(F.text == "⌫ Delete")
async def delete_last_digit(message: Message):
    user_id = message.from_user.id
    if user_id in games and games[user_id]["mode"] == "bot_thinks":
        if games[user_id]["input"]:
            games[user_id]["input"] = games[user_id]["input"][:-1]
        current = games[user_id]["input"] or "0"
        await message.answer(
            get_text(user_id, "current_number", current), 
            reply_markup=get_number_pad(user_id)
        )

@dp.message(F.text == "Отправить ✅")
@dp.message(F.text == "Send ✅")
async def check_number(message: Message):
    user_id = message.from_user.id
    if user_id not in games or games[user_id]["mode"] != "bot_thinks":
        return

    user_input = games[user_id]["input"]
    if not user_input or not user_input.isdigit():
        await message.answer(get_text(user_id, "enter_number"), reply_markup=get_number_pad(user_id))
        games[user_id]["input"] = ""
        return
        
    guess = int(user_input)
    if guess < 1 or guess > 100:
        await message.answer(get_text(user_id, "number_range"), reply_markup=get_number_pad(user_id))
        games[user_id]["input"] = ""
        return

    number = games[user_id]["number"]
    games[user_id]["attempts"] += 1
    
    previous_guesses[user_id].append(guess)
    last_guesses = previous_guesses[user_id][-3:] if len(previous_guesses[user_id]) > 0 else [guess]
    guesses_text = "➡️ ".join(str(g) for g in last_guesses)

    if guess < number:
        await message.answer(get_text(user_id, "higher", guesses_text), reply_markup=get_number_pad(user_id))
    elif guess > number:
        await message.answer(get_text(user_id, "lower", guesses_text), reply_markup=get_number_pad(user_id))
    else:
        if user_id not in user_stats:
            user_stats[user_id] = {"wins": 0, "attempts": 0, "losses": 0}
        user_stats[user_id]["wins"] += 1
        user_stats[user_id]["attempts"] += games[user_id]["attempts"]
        
        await message.answer(
            get_text(user_id, "win", number, games[user_id]['attempts']),
            reply_markup=get_main_menu(user_id)
        )
        del games[user_id]
        if user_id in previous_guesses:
            del previous_guesses[user_id]
        return

    games[user_id]["input"] = ""

# --- Пользователь загадывает число ---
@dp.message(F.text == "🎯 Я загадаю число")
@dp.message(F.text == "🎯 I'll think of a number")
async def user_thinks_mode(message: Message):
    user_id = message.from_user.id
    games[user_id] = {"mode": "user_thinks", "low": 1, "high": 100, "attempts": 0}
    await message.answer(get_text(user_id, "user_thinking"), reply_markup=get_ready_kb(user_id))

@dp.message(F.text == "✅ Готов")
@dp.message(F.text == "✅ Ready")
async def bot_guess(message: Message):
    user_id = message.from_user.id
    if user_id in games and games[user_id]["mode"] == "user_thinks":
        low = games[user_id]["low"]
        high = games[user_id]["high"]
        if low > high:
            await message.answer("🤔 Кажется, ты где-то ошибся!", reply_markup=get_main_menu(user_id))
            del games[user_id]
            return
        guess = (low + high) // 2
        games[user_id]["guess"] = guess
        games[user_id]["attempts"] += 1
        await message.answer(get_text(user_id, "bot_guess", guess), reply_markup=get_game_kb(user_id))

@dp.message(F.text == "➕ Больше")
@dp.message(F.text == "➕ Higher")
async def more(message: Message):
    user_id = message.from_user.id
    if user_id in games and games[user_id]["mode"] == "user_thinks":
        games[user_id]["low"] = games[user_id]["guess"] + 1
        await bot_guess(message)

@dp.message(F.text == "➖ Меньше")
@dp.message(F.text == "➖ Lower")
async def less(message: Message):
    user_id = message.from_user.id
    if user_id in games and games[user_id]["mode"] == "user_thinks":
        games[user_id]["high"] = games[user_id]["guess"] - 1
        await bot_guess(message)

@dp.message(F.text == "🎉 Угадал")
@dp.message(F.text == "🎉 Guessed")
async def guessed(message: Message):
    user_id = message.from_user.id
    if user_id in games and games[user_id]["mode"] == "user_thinks":
        attempts = games[user_id]["attempts"]
        number = games[user_id]["guess"]
        await message.answer(get_text(user_id, "bot_win", number, attempts), reply_markup=get_main_menu(user_id))
        del games[user_id]

# --- Обработка других сообщений ---
@dp.message()
async def handle_unknown(message: Message):
    user_id = message.from_user.id
    if user_id in games:
        mode = games[user_id]["mode"]
        if mode == "bot_thinks":
            await message.answer(get_text(user_id, "use_keyboard"), reply_markup=get_number_pad(user_id))
        elif mode == "user_thinks":
            await message.answer(get_text(user_id, "use_buttons"), reply_markup=get_game_kb(user_id))
    else:
        await message.answer(get_text(user_id, "choose_mode"), reply_markup=get_main_menu(user_id))

# --- Запуск бота ---
async def main():
    print("🤖 Бот запускается...")
    print("📱 Работает в Pydroid 3")
    print("🌐 Поддержка языков: Русский, English")
    await dp.start_polling(bot)

# Запуск для Pydroid 3
if __name__ == "__main__":
    try:
        asyncio.run(main())
    except Exception as e:
        print(f"❌ Ошибка: {e}")