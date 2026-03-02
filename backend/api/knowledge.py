import os
import json
import numpy as np
import faiss

from fastapi import APIRouter, UploadFile, File, HTTPException

from runtime.parsers.registry import ParserRegistry
from runtime.chunking import chunk_text
from runtime.embeddings import embed_texts

router = APIRouter()
registry = ParserRegistry()

AGENTS_BASE = "storage/agents"


@router.post("/agents/{agent_id}/upload")
async def upload_knowledge(agent_id: str, file: UploadFile = File(...)):

    agent_dir = os.path.join(AGENTS_BASE, agent_id)

    if not os.path.exists(agent_dir):
        raise HTTPException(status_code=404, detail="Agent not found")

    # =========================
    # Save uploaded file
    # =========================

    save_path = os.path.join(agent_dir, file.filename)

    # Optional: prevent duplicate overwrite silently
    if os.path.exists(save_path):
        os.remove(save_path)

    with open(save_path, "wb") as f:
        f.write(await file.read())

    # =========================
    # Parse file using registry
    # =========================

    try:
        parser = registry.get_parser(save_path)
        parsed_blocks = parser.parse(save_path)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Parsing failed: {str(e)}")

    # =========================
    # Load existing chunks (important fix)
    # =========================

    chunks_path = os.path.join(agent_dir, "chunks.json")

    if os.path.exists(chunks_path):
        with open(chunks_path, "r", encoding="utf-8") as f:
            existing_chunks = json.load(f)
    else:
        existing_chunks = []

    new_chunks = []

    # =========================
    # Chunk parsed content
    # =========================

    for block in parsed_blocks:
        source_name = os.path.basename(block["metadata"]["source"])
        source_type = block["metadata"]["type"]

        chunks = chunk_text(
            block["text"],
            source_name=source_name,
            source_type=source_type
        )

        new_chunks.extend(chunks)

    if not new_chunks:
        raise HTTPException(
            status_code=400,
            detail="No usable text content found in file"
        )

    # Merge old + new
    all_chunks = existing_chunks + new_chunks

    # =========================
    # Save updated chunks.json
    # =========================

    with open(chunks_path, "w", encoding="utf-8") as f:
        json.dump(all_chunks, f, indent=2, ensure_ascii=False)

    # =========================
    # Rebuild FAISS index from ALL chunks
    # =========================

    texts = [c["text"] for c in all_chunks]

    embeddings = embed_texts(texts)
    embeddings = np.array(embeddings).astype("float32")

    if embeddings.shape[0] == 0:
        raise HTTPException(status_code=500, detail="Embedding failed")

    dimension = embeddings.shape[1]

    index = faiss.IndexFlatL2(dimension)
    index.add(embeddings)

    index_path = os.path.join(agent_dir, "index.faiss")
    faiss.write_index(index, index_path)

    return {
        "status": "uploaded",
        "file": file.filename,
        "new_chunks_added": len(new_chunks),
        "total_chunks": len(all_chunks)
    }
