from datetime import datetime
from pydantic import BaseModel
from typing import List


class MemoryMessage(BaseModel):
    role: str  # "user" | "assistant"
    content: str
    timestamp: str


class ConversationMemory(BaseModel):
    agent_id: str
    user_id: str
    messages: List[MemoryMessage] = []

