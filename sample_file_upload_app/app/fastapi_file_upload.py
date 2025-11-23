# app.py
from fastapi import FastAPI, UploadFile, File, HTTPException, Depends, BackgroundTasks, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Optional
import aiofiles
import os
from pathlib import Path
import uuid

UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

app = FastAPI(title="FastAPI File Upload Demo")

# Allow local testing from any origin (adjust for production)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Small helper: save uploaded file asynchronously using chunks (prevents big-memory usage)
async def save_upload_file(upload_file: UploadFile, destination: Path, chunk_size: int = 1024*1024):
    """
    Save UploadFile.stream to disk in chunks.
    This works for both sync and async file-like backends because UploadFile.file is BytesIO/spooled file.
    """
    async with aiofiles.open(destination, "wb") as out_file:
        # Seek to beginning
        upload_file.file.seek(0)
        while True:
            chunk = await upload_file.file.read(chunk_size)
            if not chunk:
                break
            await out_file.write(chunk)

# Simple endpoint: single file upload
@app.post("/upload/single")
async def upload_single(file: UploadFile = File(...)):
    # Basic validation: content type and extension
    if not file.filename:
        raise HTTPException(400, "Empty filename")
    if file.content_type not in ("image/jpeg", "image/png", "application/pdf", "text/plain"):
        raise HTTPException(400, f"Unsupported content type: {file.content_type}")

    # Generate safe filename
    ext = Path(file.filename).suffix or ""
    dest_name = f"{uuid.uuid4().hex}{ext}"
    dest = UPLOAD_DIR / dest_name

    await save_upload_file(file, dest)
    return {"filename": file.filename, "stored_as": dest_name, "content_type": file.content_type, "size_bytes": dest.stat().st_size}

# Multiple files upload
@app.post("/upload/multiple")
async def upload_multiple(files: List[UploadFile] = File(...)):
    results = []
    for f in files:
        # simple validation
        if f.content_type not in ("image/jpeg", "image/png", "application/pdf", "text/plain"):
            raise HTTPException(400, f"Unsupported content type: {f.content_type}")
        dest = UPLOAD_DIR / f"{uuid.uuid4().hex}{Path(f.filename).suffix}"
        await save_upload_file(f, dest)
        results.append({"original": f.filename, "stored_as": dest.name, "size": dest.stat().st_size})
    return {"uploaded": results}

# Streaming read + size limit enforcement (defensive)
MAX_UPLOAD_BYTES = 10 * 1024 * 1024  # 10 MB

async def enforce_size_limit(upload_file: UploadFile, limit: int):
    total = 0
    upload_file.file.seek(0)
    while True:
        chunk = upload_file.file.read(1024*64)
        if not chunk:
            break
        if hasattr(chunk, "__await__"):
            chunk = await chunk
        total += len(chunk)
        if total > limit:
            raise HTTPException(413, f"File too large (limit {limit} bytes)")

@app.post("/upload/single_with_limit")
async def upload_single_with_limit(file: UploadFile = File(...)):
    await enforce_size_limit(file, MAX_UPLOAD_BYTES)
    dest = UPLOAD_DIR / f"{uuid.uuid4().hex}{Path(file.filename).suffix}"
    await save_upload_file(file, dest)
    return {"stored_as": dest.name, "size": dest.stat().st_size}

# Upload and process in background (e.g., virus scan, thumbnail)
async def background_process(path: Path):
    # placeholder: you would call a real scan or processing routine
    # simulate CPU/IO job here (not blocking main thread)
    # e.g., call a virus-scan tool, generate thumbnails, push to S3, etc.
    print("background processing", path)

@app.post("/upload/with_background")
async def upload_with_background(background_tasks: BackgroundTasks, file: UploadFile = File(...)):
    dest = UPLOAD_DIR / f"{uuid.uuid4().hex}{Path(file.filename).suffix}"
    await save_upload_file(file, dest)
    background_tasks.add_task(background_process, dest)
    return {"stored_as": dest.name}

# Simple health check
@app.get("/health")
def health():
    return {"status": "ok"}

# Optional: gracefully handle oversized Content-Length header (best-effort)
@app.middleware("http")
async def check_content_length(request: Request, call_next):
    content_length = request.headers.get("content-length")
    if content_length:
        try:
            if int(content_length) > (50 * 1024 * 1024):  # reject >50MB early
                return JSONResponse(status_code=413, content={"detail": "Payload too large"})
        except ValueError:
            pass
    return await call_next(request)
