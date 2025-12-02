from fastapi import FastAPI, UploadFile, File
import os

app = FastAPI()

@app.get("/health")
async def health():
    return {"status": "ok"}

UPLOAD_DIR = "uploaded_files"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    file_path = os.path.join(UPLOAD_DIR, file.filename)
    content = await file.read()
    with open(file_path, "wb") as f:
        f.write(content)
    return {"filename": file.filename, "size": len(content)}
