# 03 — User flows

API อย่างเดียว ไม่มีหน้าเว็บ (`PRODUCT.md` Platform = `api`) — flow ด้านล่างคือ journey ต่อ actor ผ่าน routes ของ `src/cellkit/app.py` และ MCP tools ของ `src/cellkit/mcp.py`

## Owner: กำหนด cron job แล้วแก้ไข (ผ่าน MCP)

```mermaid
flowchart TD
  A["MCP client calls automation.cron-job.create"] --> B["automation-mcp reads token: EMPIRE_TOKEN, EMPIRE_TOKEN_FILE or owner-mcp"]
  B --> C["POST /v1/cron-jobs with Idempotency-Key"]
  C --> D{"201 Created?"}
  D -- yes --> E["record id >= 1000000, version 1, last_status pending"]
  D -- "422 invalid_value" --> F["fix name, schedule or job_type"]
  E --> G["automation.cron-job.update with expected_version"]
  G --> H{"version matches?"}
  H -- yes --> I["PATCH applied, version + 1 (unchanged patch keeps version)"]
  H -- "409 version_conflict" --> J["get the record again and retry"]
```

## Runner script: เขียน log หลังรันงาน

```mermaid
flowchart TD
  R1["Script finishes its job, e.g. Gmail to Todoist"] --> R2["open_cell_store automation, cron-runner"]
  R2 --> R3["POST /v1/automation-log action_type=cron, description, affected_count, success, executed_at"]
  R3 --> R4{"Answer"}
  R4 -- "201" --> R5["log stored"]
  R4 -- "error or exception" --> R6["ignored by the script: best effort"]
```

## Reader: หา job ที่ล้มเหลว

```mermaid
flowchart TD
  Q1["alerts.py or decision_engine.py"] --> Q2["GET /v1/cron-jobs?last_status=failed"]
  Q2 --> Q3["platform authz decide automation.cron-job:read"]
  Q3 -- allow --> Q4["rows of the caller workspace only, RLS"]
  Q3 -- deny --> Q5["403 deny"]
  Q4 --> Q6["warning line or decision signal per failed job"]
```

## Rule / pipeline ที่มี log ผูกอยู่

```mermaid
flowchart TD
  P1["DELETE /v1/automation-rules/{id}"] --> P2{"log entries reference it?"}
  P2 -- yes --> P3["409 has_dependents"]
  P2 -- no --> P4["204 deleted"]
```

Sources: `src/cellkit/app.py` (routes, `write`, error codes), `src/cellkit/mcp.py`, `cell.yaml`, `tests/test_automation_defaults.py`, `tests/test_automation_queries.py`,
platform-ops-cli@0880abe `infra/scripts/sync/gmail_to_todoist.py`, `infra/scripts/utils/alerts.py`, `infra/scripts/workflows/decision_engine.py`

## Open questions

- ไม่มี flow "runner อ่าน cron-job แล้วอัปเดต `last_run_at` / `last_status`" ใน caller ที่พบ — ใครอัปเดตฟิลด์เหล่านี้?
