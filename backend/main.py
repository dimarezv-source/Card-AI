from __future__ import annotations

import os
import uuid
from pathlib import Path
from typing import Any

from fastapi import FastAPI, Header, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

APP_NAME = "CardAI API"
DATA_DIR = Path(os.getenv("CARDAI_DATA_DIR", "/tmp/cardai-uploads"))
MAX_UPLOAD_BYTES = int(os.getenv("CARDAI_MAX_UPLOAD_BYTES", str(15 * 1024 * 1024)))
ALLOWED_TYPES = {"image/jpeg", "image/png", "image/webp"}

app = FastAPI(title=APP_NAME, version="0.1.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
)


@app.get("/")
async def root() -> dict[str, str]:
    return {"service": APP_NAME, "status": "ok", "health": "/health"}


@app.get("/health")
async def health() -> dict[str, Any]:
    return {
        "status": "ok",
        "service": "cardai-api",
        "ai": "not_configured",
        "storage": "temporary",
    }


@app.post("/api/projects/{project_id}/photos")
async def upload_photo(
    project_id: str,
    request: Request,
    content_type: str | None = Header(default=None, alias="Content-Type"),
    x_filename: str | None = Header(default=None, alias="X-Filename"),
) -> JSONResponse:
    """Accept the raw image bytes sent by the Android client.

    This starter deliberately does not claim AI analysis is implemented. Files are
    stored in the service's local temporary directory; configure persistent object
    storage before using it for production data.
    """
    if content_type not in ALLOWED_TYPES:
        raise HTTPException(status_code=415, detail="Поддерживаются JPEG, PNG и WebP")
    body = await request.body()
    if not body:
        raise HTTPException(status_code=400, detail="Пустой файл")
    if len(body) > MAX_UPLOAD_BYTES:
        raise HTTPException(status_code=413, detail="Файл превышает допустимый размер")

    safe_project = "".join(c for c in project_id if c.isalnum() or c in "-_")[:80]
    if not safe_project:
        raise HTTPException(status_code=400, detail="Некорректный project_id")

    extension = {"image/jpeg": ".jpg", "image/png": ".png", "image/webp": ".webp"}[content_type]
    photo_id = uuid.uuid4().hex
    target_dir = DATA_DIR / safe_project
    target_dir.mkdir(parents=True, exist_ok=True)
    target = target_dir / f"{photo_id}{extension}"
    target.write_bytes(body)

    return JSONResponse(
        status_code=201,
        content={
            "ok": True,
            "status": "waiting_for_ai",
            "message": "Фото загружено; AI-модуль пока не подключён",
            "project_id": safe_project,
            "photo_id": photo_id,
            "filename": Path(x_filename or f"photo{extension}").name[:160],
            "size_bytes": len(body),
            "content_type": content_type,
        },
    )


@app.post("/api/projects/{project_id}/analyze")
async def analyze_project(project_id: str) -> dict[str, Any]:
    safe_project = "".join(c for c in project_id if c.isalnum() or c in "-_")[:80]
    folder = DATA_DIR / safe_project
    count = sum(1 for p in folder.iterdir() if p.is_file()) if folder.exists() else 0
    return {
        "ok": True,
        "status": "waiting_for_ai",
        "project_id": safe_project,
        "photos_received": count,
        "message": "Загрузка работает, но AI-модуль ещё не настроен.",
        "draft": None,
    }
