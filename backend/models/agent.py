# models/agent.py

from sqlmodel import SQLModel, Field
from typing import Optional
from datetime import datetime
import uuid


class Agent(SQLModel, table=True):
    # ===== Identity =====
    id: str = Field(
        default_factory=lambda: str(uuid.uuid4()),
        primary_key=True,
        index=True
    )

    name: str = Field(index=True)
    description: Optional[str] = None

    # ===== Behavior =====
    system_prompt: str = Field(
        default="You are a helpful knowledge-based assistant."
    )

    # JSON string for future rules / tools / constraints
    rules_json: str = Field(default="{}")

    # ===== State =====
    index_built: bool = Field(default=False)
    knowledge_items: int = Field(default=0)

    # ===== Metadata =====
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

