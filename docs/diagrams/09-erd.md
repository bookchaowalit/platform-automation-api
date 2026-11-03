# 09 — ERD

Schema `automation` จาก `migrations/0001_automation.sql` (migration เดียว) + ตาราง `public.schema_migrations` ที่ `automation-db migrate` สร้าง
ทุกตาราง PK เป็น `(workspace_id, id)` ยกเว้น `create_keys` และ `outbox`; id เริ่มที่ 1,000,000 (ช่วงต่ำกว่าสงวนให้ `legacy_id` import)

```mermaid
erDiagram
  automation_rules ||--o{ automation_log : "rule_id (workspace_id, id)"
  workflow_pipelines ||--o{ automation_log : "pipeline_id (workspace_id, id)"

  cron_jobs {
    uuid workspace_id PK
    bigint id PK
    bigint legacy_id "unique per workspace"
    text name "1-200"
    text description
    text schedule "1-200"
    text job_type "1-80"
    text params "default {}"
    boolean is_active "default true"
    timestamptz last_run_at
    timestamptz next_run_at
    text last_status "default pending, max 40"
    integer retry_count ">= 0"
    timestamptz last_retry_at
    bigint version
    timestamptz created_at
    timestamptz updated_at
  }
  automation_rules {
    uuid workspace_id PK
    bigint id PK
    bigint legacy_id
    text name "1-200"
    text description
    text trigger "required"
    text action "required"
    text project_filter "max 200"
    integer priority_filter
    text category_filter "max 200"
    boolean is_active
    integer execution_count ">= 0"
    timestamptz last_executed_at
    bigint version
    timestamptz created_at
    timestamptz updated_at
  }
  workflow_pipelines {
    uuid workspace_id PK
    bigint id PK
    bigint legacy_id
    text name "1-200"
    text description
    text steps "required"
    boolean is_active
    integer run_count ">= 0"
    timestamptz last_run_at
    bigint version
    timestamptz created_at
    timestamptz updated_at
  }
  automation_log {
    uuid workspace_id PK
    bigint id PK
    bigint legacy_id
    bigint rule_id FK
    bigint pipeline_id FK
    text action_type "1-40"
    text description "required"
    text affected_tasks "Tasks API ids, unchecked"
    integer affected_count ">= 0"
    boolean success "default true"
    text error_message
    timestamptz executed_at
    bigint version
    timestamptz created_at
    timestamptz updated_at
  }
  create_keys {
    uuid workspace_id PK
    uuid actor PK
    text kind PK "one of 4 resources"
    text key PK "8-200"
    bigint record_id
    timestamptz created_at
  }
  outbox {
    uuid id PK
    uuid workspace_id
    text type
    text subject
    uuid execution_id
    text classification "default confidential"
    jsonb payload
    timestamptz occurred_at
    timestamptz published_at
    integer attempts
    timestamptz next_attempt_at
    text last_error
    text correlation_id
  }
  schema_migrations {
    text name PK
    text sha256
    timestamptz applied_at
  }
```

หมายเหตุ:
- `create_keys.record_id` ไม่มี FK (จองไว้ก่อน execution เริ่ม)
- `outbox` ไม่มีแถวในเซลล์นี้: ไม่มี resource ไหนประกาศ `graph` ใน `cell.yaml`
- `affected_tasks` อ้าง Tasks API แบบ free text ไม่มี FK ข้าม service (`PRODUCT.md`)
- Indexes: `*_legacy` (unique partial), และ index ต่อ filter field ใน `cell.yaml`

Sources: `migrations/0001_automation.sql`, `cell.yaml`, `src/cellkit/db.py` (`migrate`), `src/cellkit/app.py` (`emit`, `reserve`), `PRODUCT.md`
