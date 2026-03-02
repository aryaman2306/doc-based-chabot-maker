import zipfile
import tempfile
import os
import json
import shutil
import uuid

from fastapi import APIRouter, UploadFile, File, HTTPException

router = APIRouter()


@router.post("/agents/import")
def import_agent(file: UploadFile = File(...)):
    if not file.filename.endswith(".zip"):
        raise HTTPException(400, "Only .zip agent exports are supported")

    new_agent_id = str(uuid.uuid4())
    agent_base = f"backend/storage/agents/{new_agent_id}"
    memory_base = f"backend/memory_data"

    os.makedirs(agent_base, exist_ok=True)

    with tempfile.TemporaryDirectory() as tmpdir:
        zip_path = os.path.join(tmpdir, "agent.zip")

        with open(zip_path, "wb") as f:
            f.write(file.file.read())

        with zipfile.ZipFile(zip_path, "r") as zipf:
            zipf.extractall(tmpdir)

        # ---- Validate manifest ----
        manifest_path = os.path.join(tmpdir, "manifest.json")
        if not os.path.exists(manifest_path):
            raise HTTPException(400, "manifest.json missing")

        with open(manifest_path, "r") as f:
            manifest = json.load(f)

        if manifest.get("version") != "1.0":
            raise HTTPException(400, "Unsupported agent export version")

        # ---- Required files ----
        required = ["agent.json", "chunks.json", "index.faiss"]
        for r in required:
            if not os.path.exists(os.path.join(tmpdir, r)):
                raise HTTPException(400, f"Missing required file: {r}")

        # ---- Move core agent files ----
        shutil.move(
            os.path.join(tmpdir, "agent.json"),
            os.path.join(agent_base, "agent.json"),
        )
        shutil.move(
            os.path.join(tmpdir, "chunks.json"),
            os.path.join(agent_base, "chunks.json"),
        )
        shutil.move(
            os.path.join(tmpdir, "index.faiss"),
            os.path.join(agent_base, "index.faiss"),
        )

        # ---- Memory (optional) ----
        if manifest.get("includes_memory"):
            memory_src = os.path.join(tmpdir, "memory.json")
            if os.path.exists(memory_src):
                shutil.move(
                    memory_src,
                    os.path.join(
                        memory_base, f"{new_agent_id}_default.json"
                    ),
                )

    return {
        "status": "imported",
        "agent_id": new_agent_id,
    }

