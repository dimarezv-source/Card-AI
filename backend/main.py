from __future__ import annotations

import base64
import os
import uuid
from pathlib import Path
from typing import Any

from fastapi import FastAPI, Header, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from openai import OpenAI, APIError, APITimeoutError

APP_NAME = "CardAI API"
DATA_DIR = Path(os.getenv("CARDAI_DATA_DIR", "/tmp/cardai-uploads"))
MAX_UPLOAD_BYTES = int(os.getenv("CARDAI_MAX_UPLOAD_BYTES", str(15 * 1024 * 1024)))
ALLOWED_TYPES = {"image/jpeg": ".jpg", "image/png": ".png", "image/webp": ".webp"}
MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
app = FastAPI(title=APP_NAME, version="0.2.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
)


def safe_project_id(project_id: str) -> str:
    safe = "".join(c for c in project_id if c.isalnum() or c in "-_")[:80]
    if not safe:
        raise HTTPException(status_code=400, detail="Некорректный project_id")
    return safe


def photo_files(project_id: str) -> list[Path]:
    folder = DATA_DIR / safe_project_id(project_id)
    if not folder.is_dir():
        return []
    return sorted(
        (p for p in folder.iterdir() if p.is_file() and p.suffix.lower() in {".jpg", ".png", ".webp"}),
        key=lambda p: p.stat().st_mtime,
    )


@app.get("/")
async def root() -> dict[str, str]:
    return {"service": APP_NAME, "status": "ok", "health": "/health"}


@app.get("/health")
async def health() -> dict[str, Any]:
    configured = bool(os.getenv("OPENAI_API_KEY", "").strip())
    return {
        "status": "ok",
        "service": "cardai-api",
        "ai": "configured" if configured else "not_configured",
        "model": MODEL if configured else None,
        "storage": "temporary",
    }


@app.post("/api/projects/{project_id}/photos")
async def upload_photo(
    project_id: str,
    request: Request,
    content_type: str | None = Header(default=None, alias="Content-Type"),
    x_filename: str | None = Header(default=None, alias="X-Filename"),
) -> JSONResponse:
    if content_type not in ALLOWED_TYPES:
        raise HTTPException(status_code=415, detail="Поддерживаются JPEG, PNG и WebP")
    body = await request.body()
    if not body:
        raise HTTPException(status_code=400, detail="Пустой файл")
    if len(body) > MAX_UPLOAD_BYTES:
        raise HTTPException(status_code=413, detail="Файл превышает допустимый размер")

    safe_project = safe_project_id(project_id)
    extension = ALLOWED_TYPES[content_type]
    photo_id = uuid.uuid4().hex
    target_dir = DATA_DIR / safe_project
    target_dir.mkdir(parents=True, exist_ok=True)
    (target_dir / f"{photo_id}{extension}").write_bytes(body)
    return JSONResponse(
        status_code=201,
        content={
            "ok": True,
            "status": "uploaded",
            "message": "Фото загружено",
            "project_id": safe_project,
            "photo_id": photo_id,
            "filename": Path(x_filename or f"photo{extension}").name[:160],
            "size_bytes": len(body),
            "content_type": content_type,
        },
    )


@app.post("/api/projects/{project_id}/analyze")
async def analyze_project(project_id: str) -> dict[str, Any]:
    safe_project = safe_project_id(project_id)
    photos = photo_files(safe_project)
    if not photos:
        raise HTTPException(status_code=400, detail="Сначала добавьте хотя бы одну фотографию")
    api_key = os.getenv("OPENAI_API_KEY", "").strip()
    if not api_key:
        raise HTTPException(
            status_code=503,
            detail="AI не настроен на сервере. Администратору нужно добавить OPENAI_API_KEY в настройках Render.",
        )

    # Limit vision payload/cost and use the most recently uploaded 6 photos.
    selected = photos[-6:]
    content: list[dict[str, Any]] = [{
        "type": "text",
        "text": (
            "Ты — эксперт по подготовке объявлений для Avito на русском языке. "
            "Проанализируй фотографии товара. Не выдумывай бренд, модель, состояние или характеристики, "
            "которые нельзя подтвердить по фото. Неопределённое отмечай как неизвестное. "
            "Верни только JSON-объект с полями: title (короткий заголовок объявления), "
            "category (предполагаемая категория), description (готовое честное описание на русском), "
            "condition (оценка состояния только по видимым признакам), price_min (целое число рублей или null), "
            "price_max (целое число рублей или null), price_reasoning (кратко почему такой диапазон и что проверить), "
            "detected_items (массив обнаруженных предметов), photo_tips (массив советов по фото), "
            "missing_info (массив уточнений продавцу), confidence (low/medium/high). "
            "Цены — ориентировочная оценка, не выдавай её за проверенную рыночную цену. "
            "Если объект неясен, честно попроси дополнительные фото/данные."
        ),
    }]
    for path in selected:
        mime = {".jpg": "image/jpeg", ".png": "image/png", ".webp": "image/webp"}[path.suffix.lower()]
        encoded = base64.b64encode(path.read_bytes()).decode("ascii")
        content.append({"type": "image_url", "image_url": {"url": f"data:{mime};base64,{encoded}", "detail": "low"}})

    try:
        client = OpenAI(api_key=api_key, timeout=90.0, max_retries=1)
        response = client.chat.completions.create(
            model=MODEL,
            messages=[
                {"role": "system", "content": "Отвечай по-русски. Будь точным и не придумывай неизвестные факты."},
                {"role": "user", "content": content},
            ],
            response_format={"type": "json_object"},
            max_tokens=1400,
        )
        raw = response.choices[0].message.content or "{}"
        import json
        draft = json.loads(raw)
        if not isinstance(draft, dict):
            raise ValueError("Model returned non-object JSON")
    except APITimeoutError:
        raise HTTPException(status_code=504, detail="Анализ занял слишком много времени. Попробуйте ещё раз.")
    except APIError:
        raise HTTPException(status_code=502, detail="Сервис AI временно недоступен. Попробуйте позже.")
    except (ValueError, TypeError):
        raise HTTPException(status_code=502, detail="Не удалось разобрать ответ AI. Попробуйте ещё раз.")

    return {
        "ok": True,
        "status": "completed",
        "project_id": safe_project,
        "photos_received": len(photos),
        "photos_analyzed": len(selected),
        "model": MODEL,
        "draft": draft,
        "message": "Анализ фотографий завершён. Проверьте сведения и цену перед публикацией.",
    }
