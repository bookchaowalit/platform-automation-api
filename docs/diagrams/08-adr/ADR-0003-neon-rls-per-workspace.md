# ADR-0003 — Own Neon PostgreSQL database with forced row-level security per workspace

- Status: accepted (retro-documented)
- Date of decision (from history): 2026-10-10 (`migrations/0001_automation.sql`)

## Decision

- ฐานข้อมูลของ cell เอง: Neon project `platform-automation-api`, database `automation`, region `aws-ap-southeast-1` (`automation-db provision`)
- ทุกตาราง (`cron_jobs`, `automation_rules`, `workflow_pipelines`, `automation_log`, `create_keys`, `outbox`) มี `workspace_id`, `ENABLE` + `FORCE ROW LEVEL SECURITY` และ policy `workspace_isolation` บน `automation.current_workspace()` (= `app.workspace_id`)
- 3 roles: `automation_migrator` (owns schema), `automation_api` (NOBYPASSRLS, NOINHERIT, owns nothing), `automation_publisher` (outbox only)
- API ตั้ง `set_config('app.workspace_id', <token ws claim>, true)` ทุก transaction

## Consequences

- workspace หนึ่งมองไม่เห็นข้อมูลอีก workspace แม้ query ผิด; FK เป็นคู่ `(workspace_id, id)` จึงอ้างข้าม workspace ไม่ได้
- Neon free quota เป็นต่อ project จึงไม่โดน quota ของ empire-platform (ops record: neon-platform-quota)

## Evidence

`migrations/0001_automation.sql`, `db/roles.sql`, `src/cellkit/db.py`, `src/cellkit/app.py` (`bound`), `README.md`, `src/cellkit/contract.py::test_workspace_isolation`
