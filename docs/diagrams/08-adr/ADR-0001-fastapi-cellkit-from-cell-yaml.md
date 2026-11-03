# ADR-0001 — FastAPI service generated from `cell.yaml`, owned in this repo (`src/cellkit`)

- Status: accepted (retro-documented)
- Date of decision (from history): 2026-10-10 (`78ad709 feat: automation cell from solo-cell-kit`); ownership moved here 2026-10-12 (`92da7fe`)

## Context

ระบบเดิมเก็บ cron jobs / rules / pipelines / log ใน SQLite ในเครื่องเดียว ไม่มีสิทธิ์และ audit กลาง (`DOCPACK/00-product-card.md` §2)

## Decision

- ประกาศ resource, field, filter และ constraint ใน `cell.yaml`; route ทั้งหมดสร้างจาก spec โดย `src/cellkit/app.py` (FastAPI + uvicorn[standard], psycopg 3)
- `src/cellkit` เป็นโค้ดของ repo นี้เอง ไม่ sync จาก generator กลาง (retired 2026-10-12; owner decision 2026-10-21: each service owns its code)

## Consequences

- เพิ่ม field = แก้ `cell.yaml` + migration ใหม่ (append-only)
- โค้ดที่ไม่ใช้ในเซลล์นี้ (publisher, `ranges`) ยังอยู่แบบ inert (`docs/cellkit-notes.md`)

## Evidence

`cell.yaml`, `pyproject.toml`, `src/cellkit/app.py`, `src/cellkit/spec.py`, `AGENTS.md`, `docs/cellkit-notes.md`, `git log` (`78ad709`, `92da7fe`)
