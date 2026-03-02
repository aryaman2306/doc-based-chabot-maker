from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List
import json
import os

from runtime.llm import call_llm
from runtime.retrieval import search_agent_index
from runtime.rate_limit import allow_request
from runtime.prompt import build_prompt

from memory.store import load_memory, add_message

router = APIRouter()


# =========================
# Request / Response Models
# =========================

class ChatRequest(BaseModel):
    question: str
    top_k: int = 3


class ChatResponse(BaseModel):
    agent_id: str
    question: str
    answer: str
    sources: List[str]


# =========================
# Chat Endpoint (Test / Live)
# =========================

@router.post("/agents/{agent_id}/chat/", response_model=ChatResponse)
def chat(agent_id: str, payload: ChatRequest):
    question = payload.question.strip()
    top_k = payload.top_k

    if not question:
        raise HTTPException(status_code=400, detail="Question cannot be empty")

    # ---- Day 7: Rate limiting ----
    if not allow_request(agent_id):
        raise HTTPException(
            status_code=429,
            detail="Rate limit exceeded. Please slow down."
        )

    # ---- Load agent config (Day 9) ----
    agent_path = f"storage/agents/{agent_id}/agent.json"
    if not os.path.exists(agent_path):
        raise HTTPException(status_code=404, detail="Agent not found")

    with open(agent_path, "r", encoding="utf-8") as f:
        agent = json.load(f)

    instructions = agent.get("instructions")
    if not instructions:
        raise HTTPException(
            status_code=500,
            detail="Agent instructions missing"
        )

    # ---- Load memory (Day 6) ----
    user_id = "default"
    memory = load_memory(agent_id, user_id)

    # ---- Retrieve relevant chunks (RAG) ----
    results = search_agent_index(
        agent_id=agent_id,
        query=question,
        top_k=top_k
    )

    if not results:
        raise HTTPException(
            status_code=400,
            detail="Agent index not built or no relevant context found"
        )

    context_blocks = []
    sources = []

    for r in results:
        context_blocks.append(r["text"])
        sources.append(r["text"])  # Day 10: structured sources

    context = "\n".join(context_blocks)

    # ---- Build prompt (Day 9 brain separation) ----
    prompt = build_prompt(
        instructions=instructions,
        context=context,
        question=question,
    )

    # ---- Call LLM (unchanged infra) ----
    try:
        answer = call_llm(prompt)
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"LLM call failed: {str(e)}"
        )

    # ---- Save memory (chat ≠ training) ----
    add_message(agent_id, user_id, "user", question)
    add_message(agent_id, user_id, "assistant", answer)

    return ChatResponse(
        agent_id=agent_id,
        question=question,
        answer=answer,
        sources=sources
    )

