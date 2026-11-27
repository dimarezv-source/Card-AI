from __future__ import annotations

import json
import os
import re
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from fastapi import APIRouter, File, HTTPException, UploadFile

router = APIRouter()
DATA_DIR = Path(os.getenv("CARDAI_DATA_DIR", "/tmp/cardai-uploads"))
MAX_UPLOAD_BYTES = int(os.getenv("CARDAI_MAX_UPLOAD_BYTES", str(15 * 1024 * 1024)))
MAX_FILES_PER_BATCH = 20
ALLOWED_TYPES = {
    "image/jpeg": ".jpg",
    "image/png": ".png",
    "image/webp": ".webp",
}
CATALOG_FIELDS = {
    "product_name", "sku", "brand", "model", "category", "description",
    "confirmed_attributes", "condition", "price", "currency", "notes", "status",
}


def _project_id(value: str) -> str:
    safe = re.sub(r"[^a-zA-Z0-9_-]", "", value)[:80]
    if not safe:
        raise HTTPException(status_code=400, detail="Некорректный project_id")
    return safe


def _folder(project_id: str) -> Path:
    return DATA_DIR / _project_id(project_id)


def _read_json(path: Path, default: Any) -> Any:
    if not path.exists():
        return default
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        raise HTTPException(status_code=500, detail=f"Не удалось прочитать {path.name}")


def _write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(json.dumps(value, ensure_ascii=False, indent=2), encoding="utf-8")
    temporary.replace(path)


def _photo_index(folder: Path) -> list[dict[str, Any]]:
    index = _read_json(folder / "photos.json", {})
    return index if isinstance(index, list) else []


@router.post("/api/projects/{project_id}/photos/batch")
async def upload_photo_batch(
    project_id: str,
    files: list[UploadFile] = File(...),
) -> dict[str, Any]:
    if not files:
        raise HTTPException(status_code=400, detail="Добавьте хотя бы одну фотографию")
    if len(files) > MAX_FILES_PER_BATCH:
        raise HTTPException(status_code=413, detail=f"За один раз можно загрузить не более {MAX_FILES_PER_BATCH} фото")

    folder = _folder(project_id)
    folder.mkdir(parents=True, exist_ok=True)
    index = _photo_index(folder)
    uploaded: list[dict[str, Any]] = []

    for upload in files:
        mime = upload.content_type or ""
        if mime not in ALLOWED_TYPES:
            raise HTTPException(status_code=415, detail=f"Неподдерживаемый формат: {upload.filename or 'файл'}")
        body = await upload.read(MAX_UPLOAD_BYTES + 1)
        if not body:
            raise HTTPException(status_code=400, detail=f"Пустой файл: {upload.filename or 'без имени'}")
        if len(body) > MAX_UPLOAD_BYTES:
            raise HTTPException(status_code=413, detail=f"Файл превышает лимит 15 МБ: {upload.filename or 'без имени'}")

        photo_id = uuid.uuid4().hex
        extension = ALLOWED_TYPES[mime]
        stored_name = f"{photo_id}{extension}"
        (folder / stored_name).write_bytes(body)
        record = {
            "photo_id": photo_id,
            "stored_name": stored_name,
            "original_filename": Path(upload.filename or f"photo{extension}").name[:160],
            "content_type": mime,
            "size_bytes": len(body),
            "uploaded_at": datetime.now(timezone.utc).isoformat(),
        }
        index.append(record)
        uploaded.append(record)

    _write_json(folder / "photos.json", index)
    return {
        "ok": True,
        "project_id": _project_id(project_id),
        "uploaded_count": len(uploaded),
        "photos": uploaded,
        "max_files_per_batch": MAX_FILES_PER_BATCH,
    }


@router.get("/api/projects/{project_id}/photos")
async def list_project_photos(project_id: str) -> dict[str, Any]:
    folder = _folder(project_id)
    records = _photo_index(folder) if folder.exists() else []
    existing = {p.name for p in folder.iterdir() if p.is_file()} if folder.exists() else set()
    photos = [item for item in records if item.get("stored_name") in existing]
    known = {item.get("stored_name") for item in photos}
    if folder.exists():
        for path in sorted(folder.iterdir()):
            if path.is_file() and path.suffix.lower() in {".jpg", ".jpeg", ".png", ".webp"} and path.name not in known:
                photos.append({
                    "photo_id": path.stem,
                    "stored_name": path.name,
                    "original_filename": None,
                    "content_type": {
                        ".jpg": "image/jpeg", ".jpeg": "image/jpeg",
                        ".png": "image/png", ".webp": "image/webp",
                    }.get(path.suffix.lower()),
                    "size_bytes": path.stat().st_size,
                    "uploaded_at": datetime.fromtimestamp(path.stat().st_mtime, timezone.utc).isoformat(),
                })
    return {"ok": True, "project_id": _project_id(project_id), "count": len(photos), "photos": photos}


@router.get("/api/projects/{project_id}/catalog")
async def get_project_catalog(project_id: str) -> dict[str, Any]:
    folder = _folder(project_id)
    catalog = _read_json(folder / "catalog.json", {
        "project_id": _project_id(project_id),
        "product": {},
        "updated_at": None,
    })
    return {"ok": True, "catalog": catalog}


@router.put("/api/projects/{project_id}/catalog")
async def save_project_catalog(project_id: str, payload: dict[str, Any]) -> dict[str, Any]:
    unknown = sorted(set(payload) - CATALOG_FIELDS)
    if unknown:
        raise HTTPException(status_code=422, detail={"message": "Неизвестные поля каталога", "fields": unknown})
    if "confirmed_attributes" in payload and not isinstance(payload["confirmed_attributes"], (dict, list)):
        raise HTTPException(status_code=422, detail="confirmed_attributes должен быть объектом или списком")
    folder = _folder(project_id)
    folder.mkdir(parents=True, exist_ok=True)
    current = _read_json(folder / "catalog.json", {})
    product = current.get("product", {}) if isinstance(current, dict) else {}
    product.update(payload)
    catalog = {
        "project_id": _project_id(project_id),
        "product": product,
        "updated_at": datetime.now(timezone.utc).isoformat(),
    }
    _write_json(folder / "catalog.json", catalog)
    return {"ok": True, "catalog": catalog}


@router.get("/api/catalog")
async def list_catalog() -> dict[str, Any]:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    products = []
    for folder in sorted(DATA_DIR.iterdir()):
        if not folder.is_dir():
            continue
        catalog = _read_json(folder / "catalog.json", None)
        if catalog:
            products.append(catalog)
    return {"ok": True, "count": len(products), "products": products}
