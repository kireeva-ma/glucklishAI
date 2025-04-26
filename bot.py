import logging
from telegram import Update, InputFile, ReplyKeyboardMarkup
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
# This is a basic set of languages you support
LANGUAGES = {
    "en": "English",
    "de": "German",
    "fr": "French",
    "es": "Spanish",
    "ru": "Russian"
}


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
        f"🎉 Welcome! You are speaking in {LANGUAGES.get(user_language, 'your native language')}. "
        "Which language would you like to learn?",
        reply_markup=reply_markup
    )


async def handle_language_selection(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    selected_language = update.message.text.lower()

    if selected_language in LANGUAGES:
        # Store the learning language for the user
        USER_LANGUAGES[user_id]["learning"] = selected_language
        await update.message.reply_text(
            f"Great choice! I'll now communicate with you in {LANGUAGES[selected_language]}.")
    else:
        await update.message.reply_text(
            "Sorry, I don't support that language. Please choose a valid language from the list.")


async def process_voice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    learning_language = USER_LANGUAGES.get(user_id, {}).get("learning", "en")

    # Process the voice message (the transcription logic will go in the brain)
    # For now, we can just reply with the user's learning language as a placeholder
    await update.message.reply_text(
        f"Processing your voice message in {LANGUAGES.get(learning_language, 'English')}...")


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    native_language = USER_LANGUAGES.get(user_id, {}).get("native", "en")

    help_text = (
        f"📝 *Help*:\n\n"
        f"Welcome to the language learning bot! Here’s what you can do:\n\n"
        f"/start - Start the language learning process.\n"
        f"/help - Display this help message.\n\n"
        f"Once you’ve selected a language, I will respond in the language you’re learning.\n\n"
        f"Your native language is: {LANGUAGES.get(native_language, 'unknown')}\n"
        f"You can always change your learning language by typing it directly (English, German, etc.).\n\n"
        f"To get the most out of this bot, just send me messages or voice recordings!"
    )

    await update.message.reply_text(help_text)


async def handle_voice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        thinking_message = await update.message.reply_text("🤔 Lass mich kurz überlegen...")

        voice = update.message.voice
        file = await context.bot.get_file(voice.file_id)
        file_path = await file.download_to_drive()

        ai_reply = process_voice(file_path)  # <--- call aiBrain!

        await thinking_message.edit_text(ai_reply)

    except Exception as e:
        logging.error(f"Error handling voice: {e}")
        await update.message.reply_text("😵‍💫 Oops! Something went wrong. Please try again!")



async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        thinking_message = await update.message.reply_text("🤔 Einen Moment...")

        user_text = update.message.text

        prompt = (
            "You are a native German-speaking barista. "
            "Speak casually and friendly. "
            "Correct user's German softly if needed.\n"
            f"User: {user_text}\nYou:"
        )

        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}]
        )
        ai_reply = response['choices'][0]['message']['content']

        await thinking_message.edit_text(ai_reply)

    except Exception as e:
        logging.error(f"Error handling text: {e}")
        await update.message.reply_text("😵‍💫 Oops! Something went wrong. Please try again!")


# --- App ---
if __name__ == '__main__':
    app = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))  # Start command
    app.add_handler(CommandHandler("help", help_command))  # Help command
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_language_selection))  # Handle language selection
    app.add_handler(MessageHandler(filters.VOICE, process_voice))  # Handle voice messages

app.run_polling()
