# 21 — Incident response

ไม่มี runbook ของ cell นี้ใน repo; flow ด้านล่างประกอบจาก alert channel และขั้น rollback/verify ที่พบจริง

```mermaid
flowchart TD
  A1["Uptime worker: /health fails, Telegram alert"] --> T
  A2["Sentry: new error event"] --> T
  A3["ops-cli alerts.py / monitor_health: failed cron jobs"] --> T
  A4["Caller sees 503 authorization_unavailable or unavailable"] --> T
  T{"Triage"}
  T -- "503 authorization_unavailable" --> P["Check empire-platform health"]
  T -- "503 unavailable" --> N["Check Neon project platform-automation-api, quota, compute"]
  T -- "deploy broke it" --> R["Railway: redeploy an earlier deployment"]
  T -- "bug in code" --> F["Failing test first (ADR-0004), fix, PR, CI green, merge to main"]
  T -- "business signal: job failed" --> J["Owner of the runner script, not this cell"]
  P --> V
  N --> V
  R --> V
  F --> V
  V["Verify /health and one authorized read"] --> PM["Postmortem: record in specs/ or architecture-docs; no template in this repo"]
```

Sources: `README.md` (rollback), `AGENTS.md` (verify after merge), `src/cellkit/app.py` (503 codes), `src/cellkit/_sentry.py`, `specs/001-l2-baseline/spec.md` (ADR-0004 test-first),
platform-uptime-worker@57f0afb `src/targets.ts`, platform-ops-cli@0880abe `infra/scripts/utils/alerts.py`, ops record: prod-baseline-monitoring-backups (2026-11-03), ops record: neon-platform-quota (2026-11-03)

## Open questions

- Postmortem อยู่ที่ไหน และมี template กลางหรือไม่
- Sentry alert rule ส่งไปช่องทางใด (Telegram/อีเมล) — ไม่พบในไฟล์
