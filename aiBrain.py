import openai
import os
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("OPENAI_API_KEY")
client = openai.OpenAI(api_key=api_key)

async def transcribe_audio(file_path):
    with open(file_path, "rb") as audio_file:
        transcription = client.audio.transcriptions.create(
            model="whisper-1",
            file=audio_file
        )
    return transcription.text

async def generate_reply(user_text):
    prompt = (
        "You are a friendly German barista. Correct mistakes softly if needed.\n"
        f"User: {user_text}\nYou:"
    )
    response = client.chat.completions.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}]
    )
    return response.choices[0].message.content


def process_voice(file_path: str) -> str:
    """
    Given a path to an audio file, transcribe it and generate a GPT reply.
    Returns the AI's answer as a string.
    """
    # transcription
    # prompt generation
    # gpt call
    # return gpt's reply