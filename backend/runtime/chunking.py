# runtime/chunking.py
import re
from typing import List


def chunk_text(
    text: str,
    chunk_size: int = 200,
    overlap: int = 50
) -> List[str]:
    """
    Simple word-based chunking with overlap.
    Deterministic and export-friendly.
    """

    if not text:
        return []

    # normalize whitespace
    text = re.sub(r"\s+", " ", text).strip()
    words = text.split()

    chunks = []
    i = 0
    n = len(words)

    while i < n:
        chunk_words = words[i:i + chunk_size]
        chunks.append(" ".join(chunk_words))

        if i + chunk_size >= n:
            break

        i += chunk_size - overlap

    return chunks

