from gemini_client import client
from google.genai import types

def transcribe_audio(audio_bytes: bytes, mime_type: str = "audio/wav") -> str:
    """Səs qeydini mətnə çevirir."""
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=[
            types.Part.from_bytes(data=audio_bytes, mime_type=mime_type),
            "Bu səs qeydində insan nə deyir? Yalnız dediyi sözləri, Azərbaycan dilində yaz. Başqa heç nə əlavə etmə."
        ]
    )
    return response.text.strip()