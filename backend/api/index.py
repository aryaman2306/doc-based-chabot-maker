# api/index.py
from fastapi import APIRouter, HTTPException
import os
import json
import faiss

from runtime.chunking import chunk_text
from runtime.embeddings import embed_texts

router = APIRouter(
    prefix="/agents/{agent_id}/index",
    tags=["Indexing"]
)

BASE_PATH = "storage/agents"


@router.post("/build")
def build_agent_index(agent_id: str):
    agent_dir = os.path.join(BASE_PATH, agent_id)
    if not os.path.exists(agent_dir):
        raise HTTPException(status_code=404, detail="Agent not found")

    texts = []

    # Read text files
    for fname in os.listdir(agent_dir):
        if fname.endswith(".txt"):
            with open(os.path.join(agent_dir, fname), "r", encoding="utf-8") as f:
                texts.append(f.read())

    # Read uploaded files
    files_dir = os.path.join(agent_dir, "files")
    if os.path.exists(files_dir):
        for fname in os.listdir(files_dir):
            with open(
                os.path.join(files_dir, fname),
                "r",
                encoding="utf-8",
                errors="ignore"
            ) as f:
                texts.append(f.read())

    if not texts:
        raise HTTPException(status_code=400, detail="No knowledge to index")

    # Chunk
    all_chunks = []
    for text in texts:
        all_chunks.extend(chunk_text(text))

    if not all_chunks:
        raise HTTPException(status_code=400, detail="Chunking failed")

    # Embed
    vectors = embed_texts(all_chunks)

    # Build FAISS
    dim = vectors.shape[1]
    index = faiss.IndexFlatL2(dim)
    index.add(vectors)

    # Save index
    faiss.write_index(index, os.path.join(agent_dir, "index.faiss"))

    # Save chunks
    with open(os.path.join(agent_dir, "chunks.json"), "w") as f:
        json.dump(all_chunks, f, indent=2)

    return {
        "agent_id": agent_id,
        "chunks": len(all_chunks),
        "dimension": dim,
        "status": "indexed"
    }

