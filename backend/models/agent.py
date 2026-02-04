# models/agent.py
from sqlmodel import SQLModel, Field
from typing import Optional
from datetime import datetime
import uuid

class Agent(SQLModel, table=True):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)
    name: str
    description: Optional[str] = None
    system_prompt: str
    rules_json: Optional[str] = "{}"
    created_at: datetime = Field(default_factory=datetime.utcnow)

