# app.py
from fastapi import FastAPI
from sqlmodel import SQLModel
from db import engine

from api.agents import router as agents_router
from api.knowledge import router as knowledge_router
from api.index import router as index_router
from api.search import router as search_router
from api.chat import router as chat_router
from api.import_agent import router as import_router
from fastapi.middleware.cors import CORSMiddleware


app = FastAPI(title="AI Agent Platform")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


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
app.include_router(chat_router)
app.include_router(import_router)
