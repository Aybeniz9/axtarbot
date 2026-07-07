from gemini_client import client
from google.genai import types

def describe_image(image_bytes: bytes, mime_type: str = "image/jpeg") -> str:
    """Şəkli təsvirə çevirir ki, sonra semantik axtarışda istifadə edilsin."""
    prompt = "Bu şəkildəki məhsulu 1-2 cümlə ilə Azərbaycan dilində təsvir et: nə növ məhsuldur, hansı mövsüm/məqsəd üçün uyğundur."

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=[
            types.Part.from_bytes(data=image_bytes, mime_type=mime_type),
            prompt
        ]
    )
    return response.text.strip()