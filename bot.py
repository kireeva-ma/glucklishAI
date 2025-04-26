import logging
from telegram import Update, InputFile
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes
import openai
from dotenv import load_dotenv
import os

from telegram.ext import CommandHandler
# Load environment variables
load_dotenv()

# Set up logging
logging.basicConfig(level=logging.INFO)

# Your API keys from environment variables
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

openai.api_key = OPENAI_API_KEY

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🎉 Willkommen! Sende mir eine Sprachnachricht, und wir üben zusammen!")

async def handle_voice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        thinking_message = await update.message.reply_text("🤔 Lass mich kurz überlegen...")

        voice = update.message.voice
        file = await context.bot.get_file(voice.file_id)
        file_path = await file.download_to_drive()

        audio_file = open(file_path, "rb")
        transcription = openai.Audio.transcribe("whisper-1", audio_file)
        user_text = transcription["text"]

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

    app.add_handler(CommandHandler("start", start))  # <-- Correct
    app.add_handler(MessageHandler(filters.VOICE, handle_voice))  # <-- Correct
    app.add_handler(MessageHandler(filters.TEXT, handle_text))

    app.run_polling()
