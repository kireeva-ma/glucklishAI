import openai
import os
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("OPENAI_API_KEY")
client = openai.OpenAI(api_key=api_key)

# from audio file to text
async def transcribe_audio(file_path):
    with open(file_path, "rb") as audio_file:
        transcription = client.audio.transcriptions.create(
            model="whisper-1",
            file=audio_file
        )
    return transcription.text

async def generate_reply_from_start(user_text, language_to_speak: str, language_level: str):
    prompt = (
        f"You are a friendly native speaker helping the user learn {language_to_speak} with {language_level} level of language proficiency.\n"
        f"Speak casually, correct mistakes softly if necessary.\n\n"
        f"Be polite and friendly.\n"
    )

    response = client.chat.completions.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}]
    )
    return response.choices[0].message.content



def process_text(user_text: str):
   prompt = (
        f"User's message: {user_text}\n"
        f"Your reply:"
   )

   response = client.chat.completions.create(
       model="gpt-4",
       messages=[{"role": "user", "content": prompt}]
   )
   return response.choices[0].message.content



def process_voice(file_path: str) -> str:
    transcription = transcribe_audio(file_path)
    replyFromAI = process_text(transcription)

    return replyFromAI


