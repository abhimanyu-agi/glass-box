"""
Voice services — Whisper transcription and OpenAI TTS.

Both call OpenAI's audio APIs. Costs are tiny (under $0.002 per voice
question round-trip) but stay capped via your platform.openai.com budget.
"""

import os
from io import BytesIO
from typing import Literal

from openai import OpenAI


# Re-uses the OPENAI_API_KEY from environment
_client: OpenAI | None = None


def _get_client() -> OpenAI:
    global _client
    if _client is None:
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise RuntimeError("OPENAI_API_KEY not set")
        _client = OpenAI(api_key=api_key)
    return _client


def transcribe(audio_bytes: bytes, filename: str = "audio.webm") -> str:
    """
    Transcribe an audio blob using Whisper.

    Browsers default to webm/opus — Whisper accepts it natively along with
    mp3, wav, m4a, ogg, etc.
    """
    client = _get_client()

    # Whisper expects a file-like object with a `name` attribute
    audio_file = BytesIO(audio_bytes)
    audio_file.name = filename

    transcript = client.audio.transcriptions.create(
        model="whisper-1",
        file=audio_file,
        response_format="text",
    )
    # `transcript` is a string when response_format="text"
    return str(transcript).strip()


# Available TTS voices from OpenAI
TtsVoice = Literal["alloy", "echo", "fable", "onyx", "nova", "shimmer"]


def synthesize_speech(text: str, voice: TtsVoice = "nova") -> bytes:
    """
    Convert text to MP3 audio using OpenAI TTS.

    Voice notes:
      - nova    : warm, professional female (recommended for exec demos)
      - alloy   : neutral, slightly androgynous
      - echo    : male, calm
      - shimmer : female, bright, slightly enthusiastic
      - onyx    : male, deeper
      - fable   : British male
    """
    client = _get_client()

    # Trim very long inputs — TTS hard limit is 4096 chars; we cap at 1500 for snappiness
    if len(text) > 1500:
        text = text[:1500].rsplit(" ", 1)[0] + "…"

    response = client.audio.speech.create(
        model="tts-1",          # tts-1-hd costs 2x and isn't perceptibly better at this length
        voice=voice,
        input=text,
        response_format="mp3",
    )

    return response.content