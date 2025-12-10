# backend/main.py
from fastapi import FastAPI, HTTPException, status, UploadFile, File, Depends
from sqlmodel import SQLModel, Field, create_engine, Session, select
from passlib.context import CryptContext
from jose import jwt
from pydantic import BaseModel
from datetime import datetime, timedelta
from typing import Optional, Generator
from pypdf import PdfReader
import os
import re
from transformers import AutoTokenizer, AutoModel
import torch
import numpy as np
import faiss

# ==== CONFIG ====
DATABASE_URL = "sqlite:///./app.db"
SECRET_KEY = os.environ.get("SECRET_KEY", "dev-secret-key-change-me")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24  # 1 day

# ==== DB SETUP ====
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False}
)

class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    username: str = Field(index=True, unique=True)
    hashed_password: str
    created_at: datetime = Field(default_factory=datetime.utcnow)

class Document(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    filename: str                     # stored filename on disk
    original_name: str                # original client filename
    content_type: Optional[str] = None
    size_bytes: int
    uploaded_at: datetime = Field(default_factory=datetime.utcnow)
    user_id: Optional[int] = Field(default=None, foreign_key="user.id")

def get_session() -> Generator[Session, None, None]:
    with Session(engine) as session:
        yield session

# ==== EMBEDDING / FAISS SETUP ====
# FAISS uses 384-d vectors for the chosen HF model (e5-small-v2)
FAISS_DIM = 384
FAISS_INDEX = faiss.IndexFlatL2(FAISS_DIM)

# HF model + tokenizer (small, ~40MB)
HF_MODEL = "intfloat/e5-small-v2"
tokenizer = AutoTokenizer.from_pretrained(HF_MODEL)
model = AutoModel.from_pretrained(HF_MODEL)

def get_embedding(text: str) -> np.ndarray:
    # e5 models often use "passage:" prefix for better embeddings
    text = "passage: " + text
    encoded = tokenizer(text, return_tensors="pt", truncation=True, padding=True)
    with torch.no_grad():
        output = model(**encoded)
        # mean pooling over token embeddings
        emb = output.last_hidden_state.mean(dim=1)
    return emb[0].cpu().numpy().astype("float32")

def embed_chunks(chunks: list[str]) -> np.ndarray:
    vectors = [get_embedding(ch) for ch in chunks]
    return np.array(vectors, dtype=np.float32)

# ==== AUTH UTILS (pbkdf2_sha256) ====
pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")

def hash_password(plain: str) -> str:
    return pwd_context.hash(plain)

def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

# ==== FASTAPI APP ====
app = FastAPI()

@app.on_event("startup")
def on_startup():
    SQLModel.metadata.create_all(engine)

@app.get("/health")
async def health():
    return {"status": "ok"}

# ---- File upload ----
UPLOAD_DIR = "uploaded_files"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@app.post("/upload")
async def upload_file(
    file: UploadFile = File(...),
    session: Session = Depends(get_session),
):
    os.makedirs(UPLOAD_DIR, exist_ok=True)

    stored_filename = file.filename
    file_path = os.path.join(UPLOAD_DIR, stored_filename)

    content = await file.read()
    size_bytes = len(content)

    with open(file_path, "wb") as f:
        f.write(content)

    doc = Document(
        filename=stored_filename,
        original_name=file.filename,
        content_type=file.content_type,
        size_bytes=size_bytes,
        user_id=None,
    )
    session.add(doc)
    session.commit()
    session.refresh(doc)

    return {
        "id": doc.id,
        "filename": doc.filename,
        "original_name": doc.original_name,
        "size_bytes": doc.size_bytes,
        "content_type": doc.content_type,
        "uploaded_at": doc.uploaded_at.isoformat(),
    }

# ---- Auth endpoints ----
class SignupSchema(BaseModel):
    username: str
    password: str

class LoginSchema(BaseModel):
    username: str
    password: str

@app.post("/signup")
def signup(payload: SignupSchema, session: Session = Depends(get_session)):
    statement = select(User).where(User.username == payload.username)
    existing = session.exec(statement).first()
    if existing:
        raise HTTPException(status_code=400, detail="Username already exists")
    user = User(username=payload.username, hashed_password=hash_password(payload.password))
    session.add(user)
    session.commit()
    session.refresh(user)
    return {"id": user.id, "username": user.username}

@app.post("/login")
def login(payload: LoginSchema, session: Session = Depends(get_session)):
    statement = select(User).where(User.username == payload.username)
    user = session.exec(statement).first()
    if not user or not verify_password(payload.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password"
        )
    token = create_access_token({"sub": user.username})
    return {"access_token": token, "token_type": "bearer"}

# ---- Documents list / chunks ----
@app.get("/documents")
def list_documents(session: Session = Depends(get_session)):
    docs = session.exec(select(Document)).all()
    return [
        {
            "id": d.id,
            "filename": d.filename,
            "original_name": d.original_name,
            "size_bytes": d.size_bytes,
            "content_type": d.content_type,
            "uploaded_at": d.uploaded_at.isoformat(),
            "user_id": d.user_id,
        }
        for d in docs
    ]

# ==== TEXT EXTRACTION & CHUNKING HELPERS ====
def extract_text_from_file(path: str) -> str:
    _, ext = os.path.splitext(path)
    ext = ext.lower()

    if ext in [".txt", ".md", ".py", ".json", ".log"]:
        with open(path, "r", encoding="utf-8", errors="ignore") as f:
            text = f.read()
    elif ext == ".pdf":
        text = ""
        with open(path, "rb") as f:
            reader = PdfReader(f)
            for page in reader.pages:
                page_text = page.extract_text() or ""
                text += page_text + "\n"
    else:
        with open(path, "rb") as f:
            raw = f.read()
        text = raw.decode("utf-8", errors="ignore")

    text = re.sub(r"\s+", " ", text).strip()
    return text

def chunk_text(text: str, chunk_size: int = 200, overlap: int = 50):
    if not text:
        return []
    words = text.split()
    chunks = []
    i = 0
    n = len(words)
    while i < n:
        chunk_words = words[i : i + chunk_size]
        chunk = " ".join(chunk_words)
        chunks.append(chunk)
        if i + chunk_size >= n:
            break
        i += chunk_size - overlap
    return chunks

@app.get("/documents/{doc_id}/chunks")
def get_document_chunks(doc_id: int, session: Session = Depends(get_session)):
    doc = session.exec(select(Document).where(Document.id == doc_id)).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    file_path = os.path.join(UPLOAD_DIR, doc.filename)
    if not os.path.exists(file_path):
        raise HTTPException(status_code=500, detail="File not found on disk")
    text = extract_text_from_file(file_path)
    chunks = chunk_text(text, chunk_size=200, overlap=50)
    return {
        "document_id": doc.id,
        "original_name": doc.original_name,
        "num_chunks": len(chunks),
        "chunks": chunks,
    }

# ==== EMBEDDING / INDEX ENDPOINTS ====
@app.post("/documents/{doc_id}/embed")
def embed_document(doc_id: int, session: Session = Depends(get_session)):
    doc = session.exec(select(Document).where(Document.id == doc_id)).first()
    if not doc:
        raise HTTPException(404, "Document not found")
    file_path = os.path.join(UPLOAD_DIR, doc.filename)
    if not os.path.exists(file_path):
        raise HTTPException(500, "File missing on disk")
    text = extract_text_from_file(file_path)
    chunks = chunk_text(text)
    if not chunks:
        raise HTTPException(400, "No text extracted from this file")
    vectors = embed_chunks(chunks)
    FAISS_INDEX.add(vectors)
    return {
        "document_id": doc_id,
        "num_chunks": len(chunks),
        "vector_dimension": int(vectors.shape[1]),
        "status": "embedded"
    }

class AskQuery(BaseModel):
    document_id: int
    query: str
    top_k: int = 3

@app.post("/ask")
def ask_document(payload: AskQuery, session: Session = Depends(get_session)):
    # embed query with HF model
    q_emb = get_embedding(payload.query).reshape(1, -1).astype(np.float32)
    distances, indices = FAISS_INDEX.search(q_emb, payload.top_k)
    # get document chunks to map indices -> text
    doc = session.exec(select(Document).where(Document.id == payload.document_id)).first()
    if not doc:
        raise HTTPException(404, "Document not found")
    text = extract_text_from_file(os.path.join(UPLOAD_DIR, doc.filename))
    chunks = chunk_text(text)
    results = []
    for idx in indices[0]:
        if 0 <= idx < len(chunks):
            results.append(chunks[idx])
    return {
        "query": payload.query,
        "top_k": payload.top_k,
        "results": results
    }

