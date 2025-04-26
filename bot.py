import logging
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes, CommandHandler
from dotenv import load_dotenv
import os
from aiBrain import generate_reply_from_start

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

    # Преобразуем код языка Telegram в стандартный формат
    user_language = LANGUAGES.get(user_language_code, 'en')

    # Сохраняем язык пользователя
    USER_LANGUAGES[user_id] = {"native": user_language, "learning": None}

    # Получаем переведенное сообщение для приветствия
    start_message = translations["start"].get(user_language, translations["start"]["en"])

    language_buttons = [[language for language in LANGUAGES.values()]]
    reply_markup = ReplyKeyboardMarkup(language_buttons, one_time_keyboard=True)

    # Отправляем сообщение на языке пользователя
    await update.message.reply_text(
        start_message.format(LANGUAGES.get(user_language, 'your native language')),
        reply_markup=reply_markup
    )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    user_language = USER_LANGUAGES.get(user_id, {}).get("native", "en")

    # Get the translated help message for the user's language
    help_message = translations["help"].get(user_language, translations["help"]["en"])

    await update.message.reply_text(help_message)


async def handle_language_selection(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    selected_language = update.message.text.lower()

    # In LANGUAGES we use language codes, so check for the code instead of the name
    selected_language_code = None
    for code, name in LANGUAGES.items():
        if name.lower() == selected_language:
            selected_language_code = code
            break

    # Check if selected language is valid
    if selected_language_code:
        # Store the learning language for the user
        USER_LANGUAGES[user_id]["learning"] = selected_language_code

        # Ask user to provide their language level
        language_levels = ["A1", "A2", "B1", "B2", "C1", "C2"]
        language_level_buttons = [
            [level for level in language_levels]
        ]
        reply_markup = ReplyKeyboardMarkup(language_level_buttons, one_time_keyboard=True)

        await update.message.reply_text(
            f"Great choice! You've selected {LANGUAGES[selected_language_code]}. "
            "Now, please tell me your language level (e.g., A1, B2, etc.).",
            reply_markup=reply_markup
        )
    else:
        await update.message.reply_text(
            "Sorry, I don't support that language. Please choose a valid language from the list."
        )


async def handle_language_level(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    selected_level = update.message.text.upper()

    valid_levels = ["A1", "A2", "B1", "B2", "C1", "C2"]

    if selected_level in valid_levels:
        # Store the language level
        USER_LANGUAGES[user_id]["language_level"] = selected_level

        await update.message.reply_text(
            f"Got it! Your level in {LANGUAGES[USER_LANGUAGES[user_id]['learning']]} is set to {selected_level}. "
            "We can now start the conversation in your learning language. Feel free to ask anything!"
        )

        # Start conversation by calling the AI function
        await generate_conversation(update, context)
    else:
        await update.message.reply_text(
            "Please choose a valid level (A1, A2, B1, B2, C1, C2)."
        )


async def generate_conversation(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    user_language = USER_LANGUAGES[user_id]["learning"]
    language_level = USER_LANGUAGES[user_id]["language_level"]

    # Call the function from aiBrains to generate the first message based on the selected language and level
    gpt_reply = await generate_reply_from_start(user_language, language_level)

    # Send the generated reply to the user
    await update.message.reply_text(gpt_reply)


# --- App ---
if __name__ == '__main__':
    app = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))  # Start command
    app.add_handler(CommandHandler("help", help_command))  # Help command
    app.add_handler(
        MessageHandler(filters.TEXT & ~filters.COMMAND, handle_language_selection))  # Handle language selection
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_language_level))  # Handle language level

    app.run_polling()
