# api/knowledge.py
from fastapi import APIRouter, UploadFile, File, HTTPException
from sqlmodel import Session, select
from pydantic import BaseModel
from db import engine
from models.knowledge import KnowledgeSource

import os
import uuid
import requests
from bs4 import BeautifulSoup

router = APIRouter(
    prefix="/agents/{agent_id}/knowledge",
    tags=["Knowledge"]
)

BASE_PATH = "storage/agents"


# ---------- FILE UPLOAD ----------
@router.post("/upload")
def upload_file(agent_id: str, file: UploadFile = File(...)):
    agent_dir = os.path.join(BASE_PATH, agent_id)
    files_dir = os.path.join(agent_dir, "files")

    if not os.path.exists(agent_dir):
        raise HTTPException(status_code=404, detail="Agent not found")

    os.makedirs(files_dir, exist_ok=True)

    filename = f"{uuid.uuid4()}_{file.filename}"
    file_path = os.path.join(files_dir, filename)

    with open(file_path, "wb") as f:
        f.write(file.file.read())

    with Session(engine) as session:
        ks = KnowledgeSource(
            agent_id=agent_id,
            type="file",
            source_name=file.filename
        )
        session.add(ks)
        session.commit()

    return {
        "message": "File uploaded successfully",
        "filename": file.filename
    }


# ---------- TEXT INGESTION ----------
class TextKnowledge(BaseModel):
    content: str
    title: str | None = None


@router.post("/text")
def add_text(agent_id: str, payload: TextKnowledge):
    agent_dir = os.path.join(BASE_PATH, agent_id)

    if not os.path.exists(agent_dir):
        raise HTTPException(status_code=404, detail="Agent not found")

    text_id = str(uuid.uuid4())
    text_path = os.path.join(agent_dir, f"text_{text_id}.txt")

    with open(text_path, "w", encoding="utf-8") as f:
        f.write(payload.content)

    with Session(engine) as session:
        ks = KnowledgeSource(
            agent_id=agent_id,
            type="text",
            source_name=payload.title or "manual_text"
        )
        session.add(ks)
        session.commit()

    return {"message": "Text knowledge added"}


# ---------- URL INGESTION ----------
class URLKnowledge(BaseModel):
    url: str


@router.post("/url")
def add_url(agent_id: str, payload: URLKnowledge):
    agent_dir = os.path.join(BASE_PATH, agent_id)

    if not os.path.exists(agent_dir):
        raise HTTPException(status_code=404, detail="Agent not found")

    try:
        response = requests.get(payload.url, timeout=10)
        response.raise_for_status()
    except Exception:
        raise HTTPException(status_code=400, detail="Failed to fetch URL")

    soup = BeautifulSoup(response.text, "html.parser")
    text = soup.get_text(separator=" ", strip=True)

    url_id = str(uuid.uuid4())
    url_path = os.path.join(agent_dir, f"url_{url_id}.txt")

    with open(url_path, "w", encoding="utf-8") as f:
        f.write(text)

    with Session(engine) as session:
        ks = KnowledgeSource(
            agent_id=agent_id,
            type="url",
            source_name=payload.url
        )
        session.add(ks)
        session.commit()

    return {"message": "URL knowledge added"}


# ---------- LIST KNOWLEDGE ----------
@router.get("/")
def list_knowledge(agent_id: str):
    with Session(engine) as session:
        items = session.exec(
            select(KnowledgeSource)
            .where(KnowledgeSource.agent_id == agent_id)
        ).all()

    return [
        {
            "id": k.id,
            "type": k.type,
            "source_name": k.source_name,
            "created_at": k.created_at.isoformat()
        }
        for k in items
    ]

