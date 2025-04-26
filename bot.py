import logging
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes, CommandHandler
from dotenv import load_dotenv
import os
import openai
from aiBrain import client
from aiBrain import process_voice

# Load environment variables
load_dotenv()

# Set up logging
logging.basicConfig(level=logging.INFO)

# Your API keys from environment variables
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

openai.api_key = OPENAI_API_KEY

USER_LANGUAGES = {}
LANGUAGES = {
    "en": "English",
    "de": "German",
    "fr": "French",
    "es": "Spanish",
    "ru": "Russian"
}

# Translations for user messages
translations = {
    "start": {
        "en": "🎉 Welcome! You are speaking in {native}. Which language would you like to learn?",
        "de": "🎉 Willkommen! Du sprichst {native}. Welche Sprache möchtest du lernen?",
        "fr": "🎉 Bienvenue ! Vous parlez {native}. Quelle langue souhaitez-vous apprendre ?",
        "es": "🎉 ¡Bienvenido! Hablas {native}. ¿Qué idioma te gustaría aprender?",
        "ru": "🎉 Добро пожаловать! Вы говорите на {native}. Какой язык вы хотите учить?"
    },
    "help": {
        "en": "📝 *Help*:\n\nWelcome to the language learning bot! Here’s what you can do:\n\n/start - Start the language learning process.\n/help - Display this help message.",
        "de": "📝 *Hilfe*:\n\nWillkommen beim Sprachlern-Bot! Hier ist, was du tun kannst:\n\n/start - Starte den Sprachlernprozess.\n/help - Zeige diese Hilfemeldung an.",
        "fr": "📝 *Aide*:\n\nBienvenue dans le bot d'apprentissage des langues ! Voici ce que vous pouvez faire:\n\n/start - Démarrez le processus d'apprentissage des langues.\n/help - Affichez ce message d'aide.",
        "es": "📝 *Ayuda*:\n\n¡Bienvenido al bot de aprendizaje de idiomas! Aquí está lo que puedes hacer:\n\n/start - Iniciar el proceso de aprendizaje de idiomas.\n/help - Mostrar este mensaje de ayuda.",
        "ru": "📝 *Помощь*:\n\nДобро пожаловать в бот для изучения языков! Вот что вы можете сделать:\n\n/start - Начать процесс обучения языку.\n/help - Показать это сообщение помощи."
    }
}

# Start command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    user_language = update.message.from_user.language_code

    # Save the user's native language for future reference
    USER_LANGUAGES[user_id] = {"native": user_language, "learning": None}

    # Ask user what language they want to learn
    language_buttons = [
        [language for language in LANGUAGES.values()]
    ]
    reply_markup = ReplyKeyboardMarkup(language_buttons, one_time_keyboard=True)

    await update.message.reply_text(
        translations["start"].get(user_language, translations["start"]["en"]).format(native=LANGUAGES.get(user_language, 'your native language')),
        reply_markup=reply_markup
    )

# Handle language selection
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
        await update.message.reply_text(
            f"Great choice! I'll now communicate with you in {LANGUAGES[selected_language_code]}."
        )
    else:
        await update.message.reply_text(
            "Sorry, I don't support that language. Please choose a valid language from the list."
        )

# Help command
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    user_language = USER_LANGUAGES.get(user_id, {}).get("native", "en")

    help_text = translations["help"].get(user_language, translations["help"]["en"])

    await update.message.reply_text(help_text)

# --- App ---
if __name__ == '__main__':
    app = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))  # Start command
    app.add_handler(CommandHandler("help", help_command))  # Help command
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_language_selection))  # Handle language selection

    app.run_polling()
