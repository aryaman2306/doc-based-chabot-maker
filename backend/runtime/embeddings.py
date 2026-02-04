# runtime/embeddings.py
from sentence_transformers import SentenceTransformer
import numpy as np

MODEL_NAME = "all-MiniLM-L6-v2"

_model = None


def get_model():
    global _model
    if _model is None:
        _model = SentenceTransformer(MODEL_NAME)
    return _model


def embed_texts(texts: list[str]) -> np.ndarray:
    """
    Returns float32 embeddings suitable for FAISS.
    """
    if not texts:
        return np.array([])

    model = get_model()
    embeddings = model.encode(
        texts,
        show_progress_bar=False,
        convert_to_numpy=True
    )

    return embeddings.astype("float32")

