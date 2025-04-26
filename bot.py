import logging
from telegram import Update, InputFile
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes
import openai
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# Set up logging
logging.basicConfig(level=logging.INFO)

# Your API keys from environment variables
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

openai.api_key = OPENAI_API_KEY

async def handle_voice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Get the voice file
    voice = update.message.voice
    file = await context.bot.get_file(voice.file_id)
    file_path = await file.download_to_drive()

    # Send file to Whisper for transcription
    audio_file = open(file_path, "rb")
    transcription = openai.Audio.transcribe("whisper-1", audio_file)
    user_text = transcription["text"]

    # Send the transcribed text to GPT with scenario context
    prompt = f"You are a native German-speaking barista. Speak casually and friendly. Correct user's German softly if needed.\nUser: {user_text}\nYou:"
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}]
    )

    ai_reply = response['choices'][0]['message']['content']

    # Send the reply back as text
    await update.message.reply_text(ai_reply)

    # (Optional: Add TTS here to reply with voice too!)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🎉 Willkommen! Sende mir eine Sprachnachricht, und wir üben zusammen!")

if __name__ == '__main__':
    app = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()

    app.add_handler(MessageHandler(filters.VOICE, handle_voice))
    app.add_handler(MessageHandler(filters.COMMAND, start))

    app.run_polling()
