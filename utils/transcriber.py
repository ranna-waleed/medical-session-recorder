import os
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))


def transcribe_audio(audio_file_path: str) -> str:
    with open(audio_file_path, "rb") as audio_file:
        transcript = client.audio.transcriptions.create(
            model="whisper-large-v3",
            file=audio_file,
            language="ar"
        )
    return transcript.text


def transcribe_with_detection(audio_file_path: str) -> dict:
    with open(audio_file_path, "rb") as audio_file:
        transcript = client.audio.transcriptions.create(
            model="whisper-large-v3",
            file=audio_file
        )
    return {
        "text": transcript.text,
        "language": "auto-detected"
    }