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


async def generate_reply_from_start(user_language: str, language_level: str):
    prompt = (
        f"You are a friendly native speaker helping the user learn {user_language} with {language_level} level of language level.\n"
        f"Speak casually, correct mistakes softly if necessary.\n\n"
        f"Be polite and friendly.\n"
        f"answer in language niveau {language_level}.\n"
    )

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": prompt}]
    )
    return response.choices[0].message.content



def process_simple_text(user_text: str):
   prompt = (
        f"User's message: {user_text}\n"
        f"Your short reply:"
   )

   response = client.chat.completions.create(
       model="gpt-4o",
       messages=[{"role": "user", "content": prompt}]
   )
   return response.choices[0].message.content

async def process_voice(file_path: str) -> str:
    transcription = await transcribe_audio(file_path)
    replyFromAI = process_simple_text(transcription)
    return replyFromAI


def process_test(language_to_speak: str, language_level: str):
    prompt = (
        f"Generate a small multiple-choice test for {language_to_speak} language for the {language_level} level of language proficiency.\n"
        f"Test must consist of 3 questions and have 4 possible answers.\n"
    )

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": prompt}]
    )
    return response.choices[0].message.content


def process_translate(user_text: str, language_of_user: str, target_language: str):
    prompt = (
        f"Translate in a friendly manner from {language_of_user} to {target_language} the following: {user_text}\n"
    )

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": prompt}]
    )
    return response.choices[0].message.content


print(process_test("German", "A1"))

