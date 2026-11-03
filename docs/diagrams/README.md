# Core 22 SDLC diagram pack — platform-automation-api

ภาพ SDLC 22 รายการตาม SDLC Diagram Catalog v2 วาดจากสิ่งที่ code และ config ของ repo นี้ทำจริง (ณ `06c72b0`, 2026-11-04)
ทุกไฟล์มี `Sources:` ใต้ diagram และ "Open questions" สำหรับสิ่งที่ยืนยันจากไฟล์ไม่ได้
Repo นี้เป็น Automation cell: API (FastAPI บน Railway serverless) + Neon database ของตัวเอง ใช้ empire-platform สำหรับ authz/executions/audit — เก็บนิยามและ log เท่านั้น ไม่รัน job

| # | Item | Status | File | Sources read |
|---|---|---|---|---|
| 01 | Business process (As-Is / To-Be) | done | [01-business-process.md](01-business-process.md) | `PRODUCT.md`, `cell.yaml`, `src/cellkit/app.py`, platform-ops-cli scripts, architecture-docs `CRON-DAG.md` |
| 02 | Use cases | done | [02-use-cases.md](02-use-cases.md) | `src/cellkit/auth.py`, `spec.py`, `mcp.py`, `importer.py`, platform-ops-cli scripts |
| 03 | User flows | done | [03-user-flows.md](03-user-flows.md) | `src/cellkit/app.py`, `mcp.py`, `tests/` |
| 04 | Traceability (RTM) | done | [04-traceability.md](04-traceability.md) | `PRODUCT.md`, `specs/001-l2-baseline/spec.md`, `tests/`, `.github/workflows/ci.yml` |
| 05 | C4 Context | done | [05-c4-context.md](05-c4-context.md) | `README.md`, `src/cellkit/*`, gateway `routes.json`, mcp-remote `worker.ts`, uptime `targets.ts` |
| 06 | C4 Container | done | [06-c4-container.md](06-c4-container.md) | `Dockerfile`, `pyproject.toml`, `.railway/railway.ts`, `.mcp.json`, `db/roles.sql` |
| 07 | C4 Component | done | [07-c4-component.md](07-c4-component.md) | `src/cellkit/*.py`, `cell.yaml` |
| 08 | ADRs | done | [08-adr/](08-adr/) — [0001](08-adr/ADR-0001-fastapi-cellkit-from-cell-yaml.md), [0002](08-adr/ADR-0002-railway-serverless-github-cd.md), [0003](08-adr/ADR-0003-neon-rls-per-workspace.md), [0004](08-adr/ADR-0004-platform-authz-executions-fail-closed.md) | `cell.yaml`, `.railway/railway.ts`, `migrations/`, `src/cellkit/auth.py`, `platform.py`, `git log` |
| 09 | ERD | done | [09-erd.md](09-erd.md) | `migrations/0001_automation.sql`, `cell.yaml`, `src/cellkit/db.py` |
| 10 | Sequences | done | [10-sequences.md](10-sequences.md) | `src/cellkit/app.py`, `auth.py`, `platform.py` |
| 11 | State machines | done | [11-state-machines.md](11-state-machines.md) | `cell.yaml`, `migrations/`, `src/cellkit/app.py`, `publisher.py`, ops-cli readers |
| 12 | API and integrations | done | [12-api-integration.md](12-api-integration.md) | `src/cellkit/app.py`, `platform.py`, `mcp.py`, `db.py`, `README.md` |
| 13 | Threat model | done | [13-threat-model.md](13-threat-model.md) | `src/cellkit/*`, `migrations/`, `db/roles.sql`, `Dockerfile`, `ci.yml` |
| 14 | Backup and DR | done | [14-backup-dr.md](14-backup-dr.md) | `PRODUCT.md`, `db.py`, platform-db-backup `README.md`, ops record prod-baseline-monitoring-backups |
| 15 | CI/CD pipeline | done | [15-cicd-pipeline.md](15-cicd-pipeline.md) | `.github/workflows/ci.yml`, `.railway/railway.ts`, `Dockerfile`, `renovate.json` |
| 16 | Deployment | done | [16-deployment.md](16-deployment.md) | `.railway/railway.ts`, `Dockerfile`, `README.md`, `server.py`, GitHub deployments API |
| 17 | Test coverage matrix | done | [17-test-coverage-matrix.md](17-test-coverage-matrix.md) | `tests/*.py`, `src/cellkit/contract.py`, `testing.py` |
| 18 | Git and release workflow | done | [18-git-release-workflow.md](18-git-release-workflow.md) | `git log`, `gh pr list`, `README.md`, `AGENTS.md` |
| 19 | Service dependency map | done | [19-service-dependency-map.md](19-service-dependency-map.md) | `src/cellkit/*`, registry `online-systems.yaml`, sibling repos |
| 20 | Observability | done | [20-observability.md](20-observability.md) | `_sentry.py`, `app.py`, uptime `targets.ts`, ops-cli `alerts.py` |
| 21 | Incident response | done | [21-incident-response.md](21-incident-response.md) | `README.md`, `AGENTS.md`, `app.py`, ops records |
| 22 | DORA | done | [22-dora.md](22-dora.md) | `git log`, `gh api …/deployments`, `gh run list` |

Reused docs (linked, not copied): [`PRODUCT.md`](../../PRODUCT.md), [`specs/001-l2-baseline/spec.md`](../../specs/001-l2-baseline/spec.md), [`docs/cellkit-notes.md`](../cellkit-notes.md), [`DOCPACK/00-product-card.md`](../../DOCPACK/00-product-card.md),
central [CRON-DAG.md](https://github.com/bookchaowalit/architecture-docs/blob/main/docs/architecture/CRON-DAG.md), [ADR-0004 TDD + SDD](https://github.com/bookchaowalit/architecture-docs/blob/main/docs/architecture/decisions/ADR-0004-tdd-sdd-standard.md), [ADR-0002 prod baseline](https://github.com/bookchaowalit/architecture-docs/blob/main/docs/architecture/decisions/ADR-0002-production-baseline-monitoring-backups.md)

Cross-repo sources read at: platform-ops-cli `0880abe`, platform-uptime-worker `57f0afb`, platform-api-gateway `1f02c2a`, platform-mcp-remote-worker `eb10b4d`, platform-mcp-aggregator `336bcea`, platform-db-backup `27a0a68`

Validate: `node ~/work/core22/tools/validate.mjs docs/diagrams/*.md docs/diagrams/08-adr/*.md`
