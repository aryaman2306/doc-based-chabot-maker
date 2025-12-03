from fastapi import FastAPI, HTTPException, status, UploadFile, File, Depends
from sqlmodel import SQLModel, Field, create_engine, Session, select
from passlib.context import CryptContext
from jose import jwt
from pydantic import BaseModel
from datetime import datetime, timedelta
from typing import Optional
import os

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
async def upload_file(file: UploadFile = File(...)):
    file_path = os.path.join(UPLOAD_DIR, file.filename)
    content = await file.read()
    with open(file_path, "wb") as f:
        f.write(content)
    return {"filename": file.filename, "size": len(content)}

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
