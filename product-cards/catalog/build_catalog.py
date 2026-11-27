#!/usr/bin/env python3
"""Build a deterministic product photo manifest from product-cards/originals."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ORIGINALS = ROOT / "originals"
OUTPUT = ROOT / "catalog" / "index.json"
IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp"}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def read_product_metadata(folder: Path) -> dict:
    metadata_file = folder / "product.json"
    if not metadata_file.exists():
        return {}
    data = json.loads(metadata_file.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError(f"{metadata_file} must contain a JSON object")
    allowed = {
        "product_name", "sku", "brand", "model", "category", "description",
        "confirmed_attributes", "condition", "price", "currency", "notes", "status",
    }
    unknown = sorted(set(data) - allowed)
    if unknown:
        raise ValueError(f"Unsupported fields in {metadata_file}: {', '.join(unknown)}")
    return data


def main() -> None:
    ORIGINALS.mkdir(parents=True, exist_ok=True)
    groups: dict[str, list[Path]] = {}
    for path in sorted(ORIGINALS.rglob("*")):
        if path.is_file() and path.suffix.lower() in IMAGE_EXTENSIONS:
            relative = path.relative_to(ORIGINALS)
            product_id = relative.parts[0] if len(relative.parts) > 1 else "_unassigned"
            groups.setdefault(product_id, []).append(path)

    products = []
    for product_id, paths in sorted(groups.items()):
        folder = ORIGINALS / product_id if product_id != "_unassigned" else ORIGINALS
        photos = []
        for path in paths:
            photos.append({
                "file_name": path.name,
                "path": path.relative_to(ROOT).as_posix(),
                "format": path.suffix.lower().lstrip("."),
                "size_bytes": path.stat().st_size,
                "sha256": sha256(path),
            })
        metadata = read_product_metadata(folder) if product_id != "_unassigned" else {}
        products.append({
            "product_id": product_id,
            **metadata,
            "photo_count": len(photos),
            "photos": photos,
        })

    manifest = {
        "schema_version": 1,
        "product_count": len(products),
        "photo_count": sum(item["photo_count"] for item in products),
        "products": products,
    }
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Catalog generated: {manifest['product_count']} products, {manifest['photo_count']} photos")


if __name__ == "__main__":
    main()
