from fastapi import FastAPI, HTTPException, status, UploadFile, File, Depends
from sqlmodel import SQLModel, Field, create_engine, Session, select
from passlib.context import CryptContext
from jose import jwt
from pydantic import BaseModel
from datetime import datetime, timedelta
from typing import Optional
from pypdf import PdfReader
import os
import re


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


def get_session():
    with Session(engine) as session:
        yield session

# ==== AUTH UTILS (pbkdf2_sha256, NOT bcrypt) ====
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

    stored_filename = file.filename  # later we can change to unique names
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

@app.get("/documents/{doc_id}/chunks")
def get_document_chunks(doc_id: int, session: Session = Depends(get_session)):
    # find document
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
# ==== TEXT EXTRACTION & CHUNKING HELPERS ====

def extract_text_from_file(path: str) -> str:
    """
    Extract text from a file based on extension.
    Supports: .txt, .md, .py, .json, .pdf
    Falls back to binary -> utf-8 decode for unknown types.
    """
    _, ext = os.path.splitext(path)
    ext = ext.lower()

    # Simple text-based files
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
        # Fallback: try treating as utf-8 text
        with open(path, "rb") as f:
            raw = f.read()
        text = raw.decode("utf-8", errors="ignore")

    # Basic cleanup: collapse whitespace
    text = re.sub(r"\s+", " ", text).strip()
    return text

def chunk_text(text: str, chunk_size: int = 200, overlap: int = 50):
    """
    Very simple word-based chunking.
    chunk_size: number of words per chunk
    overlap: overlapping words between chunks
    """
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

