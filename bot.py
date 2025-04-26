import logging
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes, CommandHandler
from dotenv import load_dotenv
import os
from aiBrain import generate_reply_from_start, process_simple_text, process_voice
import re
# Load environment variables
load_dotenv()

# Set up logging
logging.basicConfig(level=logging.INFO)

# Your API keys from environment variables
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

USER_LANGUAGES = {}
LANGUAGES = {
    "en": "English",
    "de": "German",
    "fr": "French",
    "es": "Spanish",
    "ru": "Russian"
}

# Translations for /start and /help
translations = {
    "start": {
        "en": "🎉 Welcome! You are speaking in {0}. Which language would you like to learn?",
        "de": "🎉 Willkommen! Du sprichst {0}. Welche Sprache möchtest du lernen?",
        "fr": "🎉 Bienvenue! Vous parlez {0}. Quelle langue souhaitez-vous apprendre?",
        "es": "🎉 ¡Bienvenido! Estás hablando en {0}. ¿Qué idioma te gustaría aprender?",
        "ru": "🎉 Добро пожаловать! Вы говорите на {0}. Какой язык вы хотите учить?"
    },
    "help": {
        "en": "📝 Help: /start to start. /help to get help.",
        "de": "📝 Hilfe: /start um zu starten. /help für Hilfe.",
        "fr": "📝 Aide: /start pour commencer. /help pour obtenir de l'aide.",
        "es": "📝 Ayuda: /start para comenzar. /help para obtener ayuda.",
        "ru": "📝 Помощь: /start для начала. /help для получения помощи."
    }
}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    user_language_code = update.message.from_user.language_code

    user_language = LANGUAGES.get(user_language_code, 'en')

    USER_LANGUAGES[user_id] = {"native": user_language, "learning": None, "language_level": None, "stage": "choose_language"}

    start_message = translations["start"].get(user_language, translations["start"]["en"])

    language_buttons = [[language for language in LANGUAGES.values()]]
    reply_markup = ReplyKeyboardMarkup(language_buttons, one_time_keyboard=True)

    await update.message.reply_text(
        start_message.format(LANGUAGES.get(user_language, 'your native language')),
        reply_markup=reply_markup
    )

async def test_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    user_state = USER_LANGUAGES.get(user_id)

    if not user_state or not user_state.get("learning") or not user_state.get("language_level"):
        await update.message.reply_text("Please select a language and level first with /start.")
        return

    language = LANGUAGES.get(user_state["learning"], "English")
    level = user_state["language_level"]

    test_content = process_test(language, level)

    questions = parse_test_content(test_content)

    for question in questions:
        question_text = question["question"]
        options = question["options"]

        reply_markup = ReplyKeyboardMarkup([[option] for option in options], one_time_keyboard=True, resize_keyboard=True)

        await update.message.reply_text(question_text, reply_markup=reply_markup)
import re

def parse_test_content(content: str):
    questions = []
    question_blocks = re.split(r"\n\d+\.", content)  # Делим по "1.", "2." и т.д.

    for block in question_blocks:
        block = block.strip()
        if not block:
            continue

        lines = block.split('\n')
        question = lines[0]
        options = []

        for line in lines[1:]:
            match = re.match(r"[A-D]\)\s*(.*)", line.strip())
            if match:
                options.append(match.group(1))

        if question and options:
            questions.append({
                "question": question,
                "options": options
            })

    return questions


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    user_language = USER_LANGUAGES.get(user_id, {}).get("native", "en")

    help_message = translations["help"].get(user_language, translations["help"]["en"])

    await update.message.reply_text(help_message)

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    user_state = USER_LANGUAGES.get(user_id)

    if not user_state:
        await update.message.reply_text("Please start first with /start.")
        return

    stage = user_state.get("stage")
    text = update.message.text.strip()

    if stage == "choose_language":
        await handle_language_selection(update, context)
    elif stage == "choose_level":
        await handle_language_level(update, context)
    elif stage == "conversation":
        await continue_conversation(update, context)
    else:
        await update.message.reply_text("I'm not sure what to do. Please type /start.")

async def handle_language_selection(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    selected_language = update.message.text.lower()

    selected_language_code = None
    for code, name in LANGUAGES.items():
        if name.lower() == selected_language:
            selected_language_code = code
            break

    if selected_language_code:
        USER_LANGUAGES[user_id]["learning"] = selected_language_code
        USER_LANGUAGES[user_id]["stage"] = "choose_level"

        language_levels = ["A1", "A2", "B1", "B2", "C1", "C2", "❓ "]
        language_level_buttons = [[level for level in language_levels]]
        reply_markup = ReplyKeyboardMarkup(language_level_buttons, one_time_keyboard=True, resize_keyboard=True)

        language_level_buttons = [[level for level in language_levels]]
        reply_markup = ReplyKeyboardMarkup(language_level_buttons, one_time_keyboard=True)

        await update.message.reply_text(
            f"Great choice! You've selected {LANGUAGES[selected_language_code]}. Now, please tell me your language level (e.g., A1, B2, etc.).",
            reply_markup=reply_markup
        )
    else:
        await update.message.reply_text(
            "Sorry, I don't support that language. Please choose a valid language from the list."
        )

async def handle_language_level(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    selected_level = update.message.text.strip()

    if selected_level.upper() in ["A1", "A2", "B1", "B2", "C1", "C2"]:
        USER_LANGUAGES[user_id]["language_level"] = selected_level.upper()
        USER_LANGUAGES[user_id]["stage"] = "conversation"

        learning_language = LANGUAGES[USER_LANGUAGES[user_id]['learning']]
        language_level = USER_LANGUAGES[user_id]['language_level']

        welcome_message = await generate_reply_from_start(learning_language, language_level)

        await update.message.reply_text(welcome_message)
        await continue_conversation(update, context)

    elif selected_level == "❓":
        await update.message.reply_text("Let's start a small test🚀")
        await start_test(update, context)  # вызовем функцию теста



async def start_test(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    user_state = USER_LANGUAGES.get(user_id)

    if not user_state or not user_state.get("learning"):
        await update.message.reply_text("Сначала выбери язык через /start.")
        return

    language = LANGUAGES.get(user_state["learning"], "English")
    level = "A1"  # допустим, для начала тест будет простым, потом мы можем сделать адаптивный

    test_content = process_test(language, level)
    questions = parse_test_content(test_content)

    for question in questions:
        question_text = question["question"]
        options = question["options"]

        reply_markup = ReplyKeyboardMarkup([[option] for option in options], one_time_keyboard=True, resize_keyboard=True)

        await update.message.reply_text(question_text, reply_markup=reply_markup)

async def continue_conversation(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    learning_language = USER_LANGUAGES[user_id]["learning"]
    language_level = USER_LANGUAGES[user_id]["language_level"]

    gpt_reply = process_simple_text(update.message.text, learning_language)

    await update.message.reply_text(gpt_reply)

async def handle_voice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    learning_language = USER_LANGUAGES[update.message.from_user.id]["learning"]
    try:
        voice = update.message.voice

        # Получаем файл
        new_file = await context.bot.get_file(voice.file_id)

        # Сохраняем локально
        local_file_path = f"temp_voice/{voice.file_unique_id}.ogg"
        os.makedirs(os.path.dirname(local_file_path), exist_ok=True)
        await new_file.download_to_drive(local_file_path)

        # Обрабатываем голос
        response_text = await process_voice(local_file_path, learning_language, toSpeech=False)

        # Отправляем ответ
        await update.message.reply_text(response_text)

        # Чистим файл
        os.remove(local_file_path)

    except Exception as e:
        logging.exception("An error occurred while processing a voice message")
        await update.message.reply_text("Sorry, an error occurred while processing your voice message.")


if __name__ == '__main__':
    app = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.add_handler(CommandHandler("test", test_command))
    app.add_handler(MessageHandler(filters.VOICE, handle_voice))

app.run_webhook(
    listen="0.0.0.0",
    port=int(os.environ.get('PORT', 8443)),
    webhook_url=f"https://{os.environ['RENDER_EXTERNAL_HOSTNAME']}/"

)

