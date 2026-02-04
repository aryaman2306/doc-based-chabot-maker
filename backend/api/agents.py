# api/agents.py
from fastapi import APIRouter, HTTPException
from sqlmodel import Session
from app import engine
from models.agent import Agent
import os
import json

router = APIRouter(prefix="/agents", tags=["Agents"])

AGENT_STORAGE_PATH = "storage/agents"

@router.post("/")
def create_agent(agent: Agent):
    with Session(engine) as session:
        session.add(agent)
        session.commit()
        session.refresh(agent)

    # Create agent folder
    agent_dir = os.path.join(AGENT_STORAGE_PATH, agent.id)
    os.makedirs(os.path.join(agent_dir, "files"), exist_ok=True)

    # Save exportable agent.json
    agent_json_path = os.path.join(agent_dir, "agent.json")
    with open(agent_json_path, "w") as f:
        json.dump(agent.dict(), f, indent=2, default=str)

    return {
        "agent_id": agent.id,
        "message": "Agent created successfully"
    }

