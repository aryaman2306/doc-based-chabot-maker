# models/knowledge.py
from sqlmodel import SQLModel, Field
from datetime import datetime
import uuid
from typing import Optional


class KnowledgeSource(SQLModel, table=True):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)
    agent_id: str = Field(index=True)
    type: str  # file | text | url
    source_name: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)

