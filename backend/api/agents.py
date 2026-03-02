import os
import json
import zipfile
import tempfile
from uuid import uuid4

from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse

from models.agent_config import AgentCreateRequest, AgentResponse
from runtime.agent_templates import AGENT_TEMPLATES

router = APIRouter()

AGENTS_BASE = "storage/agents"
MEMORY_BASE = "memory_data"


# =========================
# LIST AGENTS
# =========================
@router.get("/agents")
def list_agents():
    agents = []

    if not os.path.exists(AGENTS_BASE):
        return agents

    for agent_id in os.listdir(AGENTS_BASE):
        agent_dir = os.path.join(AGENTS_BASE, agent_id)
        agent_file = os.path.join(agent_dir, "agent.json")

        if os.path.isdir(agent_dir) and os.path.exists(agent_file):
            with open(agent_file, "r") as f:
                data = json.load(f)

            agents.append({
                "agent_id": agent_id,
                "name": data.get("name"),
                "agent_type": data.get("agent_type"),
            })

    return agents


# =========================
# CREATE AGENT (Day 9 CORE)
# =========================
@router.post("/agents/create", response_model=AgentResponse)
def create_agent(req: AgentCreateRequest):
    if req.agent_type not in AGENT_TEMPLATES:
        raise HTTPException(400, "Invalid agent type")

    agent_id = str(uuid4())
    agent_dir = os.path.join(AGENTS_BASE, agent_id)
    os.makedirs(agent_dir, exist_ok=True)

    instructions = AGENT_TEMPLATES[req.agent_type]["instructions"]

    agent_data = {
        "name": req.name,
        "description": req.description,
        "agent_type": req.agent_type,
        "instructions": instructions,
        "top_k": 3,
        "memory_default": "off",
    }

    with open(os.path.join(agent_dir, "agent.json"), "w") as f:
        json.dump(agent_data, f, indent=2)

    # placeholders for later days
    with open(os.path.join(agent_dir, "chunks.json"), "w") as f:
        json.dump([], f)

    return {
        "agent_id": agent_id,
        "name": req.name,
        "agent_type": req.agent_type,
    }


# =========================
# GET AGENT CONFIG
# =========================
@router.get("/agents/{agent_id}")
def get_agent(agent_id: str):
    path = os.path.join(AGENTS_BASE, agent_id, "agent.json")

    if not os.path.exists(path):
        raise HTTPException(404, "Agent not found")

    with open(path) as f:
        return json.load(f)


# =========================
# UPDATE INSTRUCTIONS (TRAINING)
# =========================
@router.put("/agents/{agent_id}/instructions")
def update_instructions(agent_id: str, instructions: str):
    path = os.path.join(AGENTS_BASE, agent_id, "agent.json")

    if not os.path.exists(path):
        raise HTTPException(404, "Agent not found")

    with open(path) as f:
        data = json.load(f)

    data["instructions"] = instructions

    with open(path, "w") as f:
        json.dump(data, f, indent=2)

    return {"status": "updated"}


# =========================
# EXPORT AGENT (unchanged)
# =========================
@router.post("/agents/{agent_id}/export")
def export_agent(agent_id: str):
    base_path = os.path.join(AGENTS_BASE, agent_id)
    memory_path = os.path.join(MEMORY_BASE, f"{agent_id}_default.json")

    if not os.path.exists(base_path):
        raise HTTPException(404, "Agent not found")

    required_files = ["agent.json", "chunks.json", "index.faiss"]
    for f in required_files:
        if not os.path.exists(os.path.join(base_path, f)):
            raise HTTPException(400, f"Missing {f}")

    with tempfile.NamedTemporaryFile(delete=False, suffix=".zip") as tmp:
        zip_path = tmp.name

    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zipf:
        for f in required_files:
            zipf.write(os.path.join(base_path, f), f)

        includes_memory = False
        if os.path.exists(memory_path):
            zipf.write(memory_path, "memory.json")
            includes_memory = True

        manifest = {
            "version": "1.0",
            "agent_id": agent_id,
            "includes_memory": includes_memory,
        }

        zipf.writestr("manifest.json", json.dumps(manifest, indent=2))

    return FileResponse(
        zip_path,
        media_type="application/zip",
        filename=f"agent_export_{agent_id}.zip",
    )

