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



def process_simple_text(user_text: str, learning_language: str):
   prompt = (
        f"User's message in {learning_language}: {user_text}\n"
        f"Your short reply {learning_language}:"
   )

   response = client.chat.completions.create(
       model="gpt-4o",
       messages=[{"role": "user", "content": prompt}]
   )
   return response.choices[0].message.content

def process_voice(file_path: str) -> str:
    transcription = transcribe_audio(file_path)
    replyFromAI = process_simple_text(transcription)

    return replyFromAI

def create_simple_question(learning_language: str):
    prompt = (
        f"Create a multiple-choice question in {learning_language} language to determiner the level of language of user:\n"
        f"- One question\n"
        f"- 4 answer options\n"
        f"- Mark the correct answer with [*] at the end\n"
    )

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": prompt}]
    )

    full_text = response.choices[0].message.content

    lines = full_text.strip().split("\n")
    question = lines[0]
    options = [line[3:].replace("[*]", "").strip() for line in lines[1:]]

    return question, options


def process_translate(user_text: str, language_of_user: str, target_language: str):
    prompt = (
        f"Translate in a friendly manner from {language_of_user} to {target_language} the following: {user_text}\n"
    )

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": prompt}]
    )
    return response.choices[0].message.content


print(create_simple_question("German"))

