from gemini_client import client

def clean_text(text: str) -> str:
    return text.strip().lower()

def get_embedding(text: str):
    text = clean_text(text)
    result = client.models.embed_content(
        model="gemini-embedding-001",
        contents=text
    )
    return result.embeddings[0].values