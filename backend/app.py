# app.py
from fastapi import FastAPI
from sqlmodel import SQLModel
from db import engine

from api.agents import router as agents_router
from api.knowledge import router as knowledge_router
from api.index import router as index_router
from api.search import router as search_router

app = FastAPI(title="AI Agent Platform")

@app.on_event("startup")
def on_startup():
    SQLModel.metadata.create_all(engine)

@app.get("/health")
def health():
    return {"status": "ok"}

app.include_router(agents_router)
app.include_router(knowledge_router)
app.include_router(index_router)
app.include_router(search_router)

