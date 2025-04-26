import logging
from telegram import Update, InputFile
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes
import openai
from dotenv import load_dotenv
import os

from telegram.ext import CommandHandler

from aiBrain import client

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

        with open(file_path, "rb") as audio_file:
            transcription = client.audio.transcriptions.create(
                model="whisper-1",
                file=audio_file
            )

        user_text = transcription.text
        print(user_text)

        prompt = (
            "You are a native German-speaking barista. "
            "Speak casually and friendly. "
            "Correct user's German softly if needed.\n"
            f"User: {user_text}\nYou:"
        )

        response = client.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}]
        )

        ai_reply = response.choices[0].message.content

        await thinking_message.edit_text(ai_reply)

    except Exception as e:
        logging.error(f"Error handling voice: {e}")
        await update.message.reply_text("😵‍💫 Oops! Something went wrong. Please try again!")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.message.text
    if message.lower() == "hi" or message.lower() == "hello":
        await update.message.reply_text("👋 Hallo! Wie kann ich dir helfen?")
    else:
        await update.message.reply_text("🧑‍💻 Ich bin dein Sprachassistent. Sende mir eine Sprachnachricht, um zu üben!")

def process_voice(file_path: str) -> str:
    """
    Given a path to an audio file, transcribe it and generate a GPT reply.
    Returns the AI's answer as a string.
    """
    # transcription
    # prompt generation
    # gpt call
    # return gpt's reply

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    help_text = (
        "📚 *How to use the bot:*\n\n"
        "/start - Start the conversation.\n"
        "Send a voice message for transcription and correction.\n"
        "If you need help, type /help."
    )
    await update.message.reply_text(help_text, parse_mode="Markdown")


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
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(MessageHandler(filters.TEXT, handle_message))  # Handle all regular messages

    app.run_polling()
