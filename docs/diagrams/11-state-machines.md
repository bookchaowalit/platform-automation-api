# 11 — State machines

ไม่มี enum หรือ transition rule ในโค้ด: `last_status`, `job_type`, `action_type` เป็น free text (`PRODUCT.md`) — API ไม่บังคับลำดับสถานะ
สิ่งที่ code บังคับจริงคือ default, flag `is_active`, version และ lifecycle ของ write execution

## cron_jobs.last_status (ค่าที่โค้ดรู้จัก)

ค่า `pending` เป็น default ใน `cell.yaml`/migration; ค่า `failed` และ `error` คือค่าที่ readers ใน platform-ops-cli ใช้กรอง/นับ ไม่มีค่าอื่นที่ถูกอ้างในโค้ด

```mermaid
stateDiagram-v2
  [*] --> pending: create (default)
  pending --> other: PATCH last_status (any text up to 40)
  pending --> failed: PATCH last_status=failed
  other --> failed: PATCH
  failed --> other: PATCH
  note right of failed
    alerts.py and decision_engine.py list
    last_status=failed; monitor_health.py
    counts failed or error
  end note
```

## is_active (cron_jobs, automation_rules, workflow_pipelines)

```mermaid
stateDiagram-v2
  [*] --> active: create (default true)
  active --> paused: PATCH is_active=false
  paused --> active: PATCH is_active=true
  active --> [*]: DELETE (rule or pipeline refused with 409 while log entries exist)
  paused --> [*]: DELETE
```

## Write execution (ทุก resource)

```mermaid
stateDiagram-v2
  [*] --> prechecked: authz decide allow
  prechecked --> local_change: row changed in open transaction
  local_change --> refused: 409 or 422 from constraints, rollback
  local_change --> running: POST /v1/executions 201
  running --> committed: COMMIT
  running --> replay_returned: replayed and succeeded, rollback
  committed --> finished: finish succeeded
  committed --> finish_failed: finish error, Sentry capture
  refused --> [*]
  finished --> [*]
  finish_failed --> [*]
  replay_returned --> [*]
```

## outbox row (inert in this cell)

```mermaid
stateDiagram-v2
  [*] --> pending_publish: emit, only for graph resources
  pending_publish --> published: publish ok, published_at set
  pending_publish --> backoff: publish error, attempts + 1, next_attempt_at up to 600 s
  backoff --> pending_publish: next_attempt_at reached
  published --> [*]
```

Sources: `cell.yaml`, `migrations/0001_automation.sql`, `PRODUCT.md`, `src/cellkit/app.py` (`write`, `emit`, update/delete), `src/cellkit/publisher.py`,
platform-ops-cli@0880abe `infra/scripts/utils/alerts.py`, `infra/scripts/workflows/decision_engine.py`, `infra/scripts/platform/monitor_health.py`

## Open questions

- ชุดค่า `last_status` ที่ runner ใช้จริงคืออะไร (เช่น `success`, `running`)? ควรเป็น enum หรือไม่
