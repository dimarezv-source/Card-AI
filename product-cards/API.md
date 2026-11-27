# CardAI intake and product catalog API

All endpoints are served by the existing FastAPI service. Base URL is the deployed CardAI API URL.

## Upload a batch of source photos

`POST /api/projects/{project_id}/photos/batch`

Content type: `multipart/form-data`; repeat the `files` field for each photo.

Limits:
- Up to 20 photos per request.
- JPEG, PNG and WebP only.
- 15 MiB maximum per photo (controlled by `CARDAI_MAX_UPLOAD_BYTES`).
- Uploads are stored under the project's data folder with generated safe filenames; the original filename is kept in the photo index.

Example:

```bash
curl -X POST "$CARDAI_API/api/projects/demo-001/photos/batch" \
  -F "files=@front.jpg" \
  -F "files=@back.jpg" \
  -F "files=@label.png"
```

## List source photos

`GET /api/projects/{project_id}/photos`

Returns photo IDs, stored filenames, original filenames (when known), MIME types, byte sizes and upload timestamps.

## Read and update product catalog entry

`GET /api/projects/{project_id}/catalog`

`PUT /api/projects/{project_id}/catalog`

The PUT request accepts a partial JSON object. Supported fields:

- `product_name`
- `sku`
- `brand`
- `model`
- `category`
- `description`
- `confirmed_attributes` (object or list)
- `condition`
- `price`
- `currency`
- `notes`
- `status`

Example:

```bash
curl -X PUT "$CARDAI_API/api/projects/demo-001/catalog" \
  -H "Content-Type: application/json" \
  -d '{
    "product_name": "Название товара",
    "category": "Категория",
    "confirmed_attributes": {"Материал": "сталь"},
    "status": "draft"
  }'
```

Partial updates preserve fields omitted from the request. Unknown fields are rejected.

## List catalog entries

`GET /api/catalog`

Returns all product records currently present in the service data directory.

## Current storage limitation — read before production use

This first intake implementation stores photo files and JSON metadata in `CARDAI_DATA_DIR`, defaulting to `/tmp/cardai-uploads`. The current Render configuration does not provision persistent storage. Therefore data is temporary and may disappear when the service restarts or redeploys. This is a working intake/API foundation, **not yet durable product storage**.

Do not upload confidential or personal material. Before relying on the catalog as the permanent source of truth, connect a persistent storage provider. No paid storage or paid export is enabled by this change.
