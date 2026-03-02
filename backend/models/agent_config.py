from pydantic import BaseModel
from typing import Literal, Optional

AgentType = Literal["faq", "knowledge", "support"]

class AgentCreateRequest(BaseModel):
    name: str
    agent_type: AgentType
    description: Optional[str] = None


class AgentResponse(BaseModel):
    agent_id: str
    name: str
    agent_type: AgentType

