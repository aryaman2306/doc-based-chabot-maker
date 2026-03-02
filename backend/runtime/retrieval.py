# backend/runtime/retrieval.py

import os
import json
import faiss
import numpy as np
from sentence_transformers import SentenceTransformer

# ======================
# CONFIG
# ======================

BASE_AGENT_DIR = "storage/agents"
EMBED_MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"

embedder = SentenceTransformer(EMBED_MODEL_NAME)


# ======================
# PATH HELPERS
# ======================

def agent_dir(agent_id: str) -> str:
    return os.path.join(BASE_AGENT_DIR, agent_id)


def index_path(agent_id: str) -> str:
    return os.path.join(agent_dir(agent_id), "index.faiss")


def chunks_path(agent_id: str) -> str:
    return os.path.join(agent_dir(agent_id), "chunks.json")


# ======================
# SEARCH AGENT INDEX
# ======================

def search_agent_index(agent_id: str, query: str, top_k: int = 3):

    if not query or not query.strip():
        return []

    idx_path = index_path(agent_id)
    ch_path = chunks_path(agent_id)

    if not os.path.exists(idx_path) or not os.path.exists(ch_path):
        return []

    # ---- Load FAISS index ----
    try:
        index = faiss.read_index(idx_path)
    except Exception:
        return []

    # ---- Load chunks ----
    try:
        with open(ch_path, "r", encoding="utf-8") as f:
            chunks = json.load(f)
    except Exception:
        return []

    if not chunks:
        return []

    # ---- Embed query ----
    query_vec = embedder.encode([query], convert_to_numpy=True)
    query_vec = np.array(query_vec).astype("float32")

    # ---- Search ----
    distances, indices = index.search(query_vec, top_k)

    results = []

    for rank, idx in enumerate(indices[0]):

        if idx < 0 or idx >= len(chunks):
            continue

        chunk = chunks[idx]

        # Normalize structure
        if isinstance(chunk, str):
            # Old format (very early versions)
            results.append({
                "id": None,
                "text": chunk,
                "source": None,
                "type": None,
                "score": float(distances[0][rank])
            })
        else:
            results.append({
                "id": chunk.get("id"),
                "text": chunk.get("text"),
                "source": chunk.get("source"),
                "type": chunk.get("type"),
                "score": float(distances[0][rank])
            })

    return results
