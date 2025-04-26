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


def process_daily_challenge(learning_language: str):
    prompt = (
        f"You are a kind and friendly native-speaking teacher helping the user learn {learning_language}.\n"
        f"Generate a daily challenge for the user to practice their {learning_language} skills.\n"
        f"The challenge should be engaging, fun, and suitable for a {learning_language} learner.\n"
        f"Include a brief explanation of the challenge and its purpose.\n"
        f"Your reply should be entirely in {learning_language}."
        f"Challange must not be too big, it should be possible to do in 5-10 minutes.\n"
        f"Make challanges so that you are able to provide answers after user answers the challenge.\n"
        f"Again, please respond only in the {learning_language} language.\n"
    )

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": prompt}]
    )
    return response.choices[0].message.content






