# backend/runtime/chunking.py

from typing import List
from uuid import uuid4


def chunk_text(
    text: str,
    source_name: str,
    source_type: str,
    chunk_size: int = 500,
    overlap: int = 50,
) -> List[dict]:
    """
    Splits text into overlapping chunks and attaches metadata.

    source_name: filename or URL
    source_type: "text" | "pdf" | "json" | etc
    """

    chunks = []
    start = 0
    text_length = len(text)

    if not text or not text.strip():
        return chunks

    while start < text_length:
        end = start + chunk_size
        chunk_body = text[start:end].strip()

        if chunk_body:
            chunks.append(
                {
                    "id": str(uuid4()),   # globally unique
                    "text": chunk_body,
                    "source": source_name,
                    "type": source_type,
                }
            )

        start = end - overlap

        if start < 0:
            start = 0

    return chunks
