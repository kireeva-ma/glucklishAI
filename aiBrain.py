import openai
import os
from dotenv import load_dotenv
from io import BytesIO


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
        f"You are a kind and friendly native-speaking teacher helping the user learn {user_language} at a {language_level} level.\n"
        f"Engage in casual, natural conversations with the user.\n"
        f"Gently correct any mistakes they make, but do not overwhelm them with corrections.\n"
        f"Only correct important mistakes that affect understanding or communication.\n"
        f"Always be polite, supportive, and encouraging.\n"
        f"Respond exclusively in {user_language}, using vocabulary and grammar appropriate for {language_level} learners.\n"
    )

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": prompt}]
    )
    return response.choices[0].message.content



def process_simple_text(user_text: str, learning_language: str):
   prompt = (
        f"User's message in {learning_language}: {user_text}\n"
        f"You are a kind and friendly native-speaking teacher helping the user learn {learning_language}.\n"
        f"Casually correct any mistakes they make, but do not overwhelm them with corrections.\n"
        f"Under no circumstances should you respond in any language other than {learning_language}.\n"
        f"Your reply should be short, natural, and entirely in {learning_language}.\n"
        f"At the end of your reply, briefly summarize any mistakes and add a smiley emoji.\n"
        f"If possible, ask a simple follow-up question in {learning_language} related to the topic."
   )

   response = client.chat.completions.create(
       model="gpt-4o",
       messages=[{"role": "user", "content": prompt}]
   )
   return response.choices[0].message.content


async def process_voice(file_path: str, learning_language: str, toSpeech: bool):
    transcription = await transcribe_audio(file_path)
    replyFromAI = process_simple_text(transcription, learning_language)

    if toSpeech:
        audio_bytes = text_to_audio(replyFromAI, learning_language)
        return audio_bytes
    else:
        return replyFromAI

def text_to_audio(replyFromAI: str, learning_language: str):
    voices = {
        "English": "nova",
        "German": "echo",
        "French": "fable",
        "Spanish": "onyx",
        "Russian": "shimmer",
        "Ukrainian": "echo",
    }

    # pick voice
    voice = voices.get(learning_language, "nova")

    # Create speech with OpenAI
    response = openai.audio.speech.create(
        model="tts-1",  # or "tts-1-hd" (higher quality but bigger)
        input=replyFromAI,
        voice=voice,
        response_format="mp3"
    )

    return response.content


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
        f"Translate in a friendly manner from {language_of_user} to {target_language} the following text: {user_text}\n"
    )

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": prompt}]
    )
    return response.choices[0].message.content



