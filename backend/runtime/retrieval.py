# runtime/retrieval.py
import os
import json
import faiss
import numpy as np

from runtime.embeddings import embed_texts

BASE_PATH = "storage/agents"


def load_agent_index(agent_id: str):
    agent_dir = os.path.join(BASE_PATH, agent_id)

    index_path = os.path.join(agent_dir, "index.faiss")
    chunks_path = os.path.join(agent_dir, "chunks.json")

    if not os.path.exists(index_path) or not os.path.exists(chunks_path):
        raise FileNotFoundError("Agent index not built")

    index = faiss.read_index(index_path)

    with open(chunks_path, "r", encoding="utf-8") as f:
        chunks = json.load(f)

    return index, chunks


def retrieve_chunks(agent_id: str, query: str, top_k: int = 3):
    index, chunks = load_agent_index(agent_id)

    query_vec = embed_texts([query])
    query_vec = np.array(query_vec, dtype="float32")

    distances, indices = index.search(query_vec, top_k)

    results = []
    for idx in indices[0]:
        if 0 <= idx < len(chunks):
            results.append(chunks[idx])

    return results

