# api/search.py
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from runtime.retrieval import search_agent_index

router = APIRouter(
    prefix="/agents/{agent_id}/search",
    tags=["Retrieval"]
)


class SearchQuery(BaseModel):
    query: str
    top_k: int = 3


@router.post("/")
def search_agent(agent_id: str, payload: SearchQuery):
    try:
        results = retrieve_chunks(
            agent_id=agent_id,
            query=payload.query,
            top_k=payload.top_k
        )
    except FileNotFoundError:
        raise HTTPException(status_code=400, detail="Agent index not built")

    return {
        "agent_id": agent_id,
        "query": payload.query,
        "top_k": payload.top_k,
        "results": results
    }

