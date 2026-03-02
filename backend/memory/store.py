import os
import json
from datetime import datetime
from .schema import ConversationMemory, MemoryMessage

MEMORY_DIR = "memory_data"
os.makedirs(MEMORY_DIR, exist_ok=True)


def _memory_path(agent_id: str, user_id: str) -> str:
    return os.path.join(MEMORY_DIR, f"{agent_id}_{user_id}.json")


def load_memory(agent_id: str, user_id: str) -> ConversationMemory:
    path = _memory_path(agent_id, user_id)
    if not os.path.exists(path):
        return ConversationMemory(agent_id=agent_id, user_id=user_id)

    with open(path, "r") as f:
        data = json.load(f)
        return ConversationMemory(**data)


def save_memory(memory: ConversationMemory):
    path = _memory_path(memory.agent_id, memory.user_id)
    with open(path, "w") as f:
        json.dump(memory.dict(), f, indent=2)


def add_message(agent_id: str, user_id: str, role: str, content: str):
    memory = load_memory(agent_id, user_id)
    memory.messages.append(
        MemoryMessage(
            role=role,
            content=content,
            timestamp=datetime.utcnow().isoformat()
        )
    )

    # keep last 10 messages only (short-term memory)
    memory.messages = memory.messages[-10:]

    save_memory(memory)

