import os
import re
import logging
import asyncio
from dotenv import load_dotenv
from telegram import Update, ReplyKeyboardMarkup, BotCommand
from telegram.ext import (
    ApplicationBuilder, MessageHandler, filters, ContextTypes, CommandHandler
)
from aiBrain import generate_reply_from_start, process_simple_text, process_voice

# Load environment variables
load_dotenv()

# Set up logging
logging.basicConfig(level=logging.INFO)

# Bot token
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

# User state storage
USER_LANGUAGES = {}

# Supported languages
LANGUAGES = {
    "en": "English",
    "de": "German",
    "fr": "French",
    "es": "Spanish",
    "ru": "Russian",
    "ua": "Ukrainian"
}

# Translations
translations = {
    "start": {
        "en": "🎉 Welcome! You are speaking in {0}. Which language would you like to learn?",
        "de": "🎉 Willkommen! Du sprichst {0}. Welche Sprache möchtest du lernen?",
        "fr": "🎉 Bienvenue! Vous parlez {0}. Quelle langue souhaitez-vous apprendre?",
        "es": "🎉 ¡Bienvenido! Estás hablando en {0}. ¿Qué idioma te gustaría aprender?",
        "ru": "🎉 Добро пожаловать! Вы говорите на {0}. Какой язык вы хотите учить?",
        "ua": "🎉 Вітаю! Ви розмовляєте {0}. Яку мову ви хочете вивчити?"
    },
    "help": {
        "en": "👩‍🏫 This bot is your personal language teacher! Use /start to set your language and level. Then just talk to me in your chosen language.",
        "de": "👩‍🏫 Dieser Bot ist dein persönlicher Sprachlehrer! Verwende /start, um deine Sprache und dein Niveau einzustellen. Danach kannst du einfach mit mir in der gewählten Sprache sprechen.",
        "fr": "👩‍🏫 Ce bot est ton professeur de langues personnel ! Utilise /start pour choisir ta langue et ton niveau. Ensuite, parle-moi simplement dans ta langue choisie.",
        "es": "👩‍🏫 ¡Este bot es tu profesor personal de idiomas! Usa /start para configurar tu idioma y nivel. Luego simplemente habla conmigo en el idioma elegido.",
        "ru": "👩‍🏫 Этот бот — твой персональный учитель языков! Используй /start, чтобы выбрать язык и уровень. Потом просто общайся со мной на выбранном языке.",
        "ua": "👩‍🏫 Цей бот — твій персональний вчитель мов! Використовуй /start, щоб вибрати мову та рівень. Потім просто спілкуйся зі мною обраною мовою."
    }
}

# Handlers
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    user_language_code = update.message.from_user.language_code
    user_language = LANGUAGES.get(user_language_code, 'en')

    USER_LANGUAGES[user_id] = {
        "native": user_language,
        "learning": None,
        "language_level": None,
        "stage": "choose_language"
    }

    start_message = translations["start"].get(user_language, translations["start"]["en"])
    language_buttons = [[language for language in LANGUAGES.values()]]
    reply_markup = ReplyKeyboardMarkup(language_buttons, one_time_keyboard=True)

    await update.message.reply_text(
        start_message.format(LANGUAGES.get(user_language, 'your native language')),
        reply_markup=reply_markup
    )

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

    selected_language_code = next((code for code, name in LANGUAGES.items() if name.lower() == selected_language), None)

    if selected_language_code:
        USER_LANGUAGES[user_id]["learning"] = selected_language_code
        USER_LANGUAGES[user_id]["stage"] = "choose_level"

        language_levels = ["A1", "A2", "B1", "B2", "C1", "C2"]
        reply_markup = ReplyKeyboardMarkup([[level for level in language_levels]], one_time_keyboard=True)

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
    selected_level = update.message.text.strip().upper()

    if selected_level in ["A1", "A2", "B1", "B2", "C1", "C2"]:
        USER_LANGUAGES[user_id]["language_level"] = selected_level
        USER_LANGUAGES[user_id]["stage"] = "conversation"

        learning_language = LANGUAGES[USER_LANGUAGES[user_id]['learning']]
        language_level = USER_LANGUAGES[user_id]['language_level']

        welcome_message = await generate_reply_from_start(learning_language, language_level)
        await update.message.reply_text(welcome_message)
        await continue_conversation(update, context)
    else:
        await update.message.reply_text("Please choose a valid level: A1, A2, B1, B2, C1, or C2.")

async def continue_conversation(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    learning_language = USER_LANGUAGES[user_id]["learning"]

    gpt_reply = process_simple_text(update.message.text, learning_language)
    await update.message.reply_text(gpt_reply)

async def handle_voice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    learning_language_code = USER_LANGUAGES[user_id]["learning"]
    learning_language = LANGUAGES[learning_language_code]

    try:
        voice = update.message.voice
        new_file = await context.bot.get_file(voice.file_id)
        local_file_path = f"temp_voice/{voice.file_unique_id}.ogg"
        os.makedirs(os.path.dirname(local_file_path), exist_ok=True)
        await new_file.download_to_drive(local_file_path)

        response_text = await process_voice(local_file_path, learning_language, toSpeech=True)

        if isinstance(response_text, bytes):
            from io import BytesIO
            audio_io = BytesIO(response_text)
            audio_io.name = "reply.mp3"
            await update.message.reply_audio(audio_io)
        else:
            await update.message.reply_text(response_text)

        os.remove(local_file_path)

    except Exception as e:
        logging.exception("Error while processing voice message")
        await update.message.reply_text("Sorry, an error occurred while processing your voice message.")

async def set_commands(app):
    await app.bot.set_my_commands([
        BotCommand("start", "Start a new conversation"),
        BotCommand("help", "How to use your personal language tutor 🤖")
    ])

def parse_test_content(content: str):
    questions = []
    blocks = re.split(r"\n\d+\.", content)

    for block in blocks:
        block = block.strip()
        if not block:
            continue
        lines = block.split('\n')
        question = lines[0]
        options = [re.match(r"[A-D]\)\s*(.*)", line).group(1) for line in lines[1:] if re.match(r"[A-D]\)\s*(.*)", line)]
        if question and options:
            questions.append({"question": question, "options": options})

    return questions

async def main():
    app = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.add_handler(MessageHandler(filters.VOICE, handle_voice))

    await set_commands(app)
    await app.run_webhook(
        listen="0.0.0.0",
        port=int(os.environ.get('PORT', 8443)),
        webhook_url=f"https://{os.environ['RENDER_EXTERNAL_HOSTNAME']}/"
    )

if __name__ == '__main__':
    asyncio.run(main())
