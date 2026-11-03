# 20 — Observability

```mermaid
flowchart LR
  API["automation-api"]
  subgraph Signals["Signals emitted"]
    LOG["stdout JSON logs: automation.write, automation.finish_failed, automation.inline_publish_failed"]
    CID["X-Correlation-Id on every response, forwarded to platform executions"]
    ERR["Sentry errors: unhandled + capture() on finish or publish failure"]
    HL["/health"]
  end
  RL["Railway logs"]
  SN["Sentry project, org personal-yu0"]
  UW["platform-uptime-worker, hourly probe because the service sleeps"]
  TG["Telegram book_noti_bot"]
  AUD["empire-platform executions and audit"]
  MH["ops-cli monitor_health cron_check, alerts.py"]

  API --> LOG --> RL
  API --> ERR --> SN
  API --> CID --> AUD
  HL --> UW --> TG
  MH -- "reads cron-jobs last_status failed" --> API
```

| Watched | How | หลักฐาน |
|---|---|---|
| Up / down | uptime worker target `automation-api`, sleeping → probed hourly, alert Telegram | platform-uptime-worker `src/targets.ts`, ops record: prod-baseline-monitoring-backups |
| Errors | Sentry เมื่อ `SENTRY_DSN` ตั้งไว้; tracing off, ไม่มี PII | `src/cellkit/_sentry.py`, `README.md` |
| Writes / audit | execution ต่อการเขียน + JSON log | `src/cellkit/app.py` |
| Failed jobs (business signal) | ops-cli อ่าน `last_status=failed` | platform-ops-cli `alerts.py`, `monitor_health.py` |
| Metrics (latency, 5xx) | **ไม่มี** — `PRODUCT.md` Measures "Proposed (nothing collects these yet)" | `PRODUCT.md` |
| Heartbeat | ไม่มี (cell ไม่มี cron job ของตัวเอง) | `.railway/railway.ts` |

Sources: `src/cellkit/app.py`, `src/cellkit/_sentry.py`, `src/cellkit/publisher.py`, `README.md`, `PRODUCT.md`, `.railway/railway.ts`, platform-uptime-worker@57f0afb `src/targets.ts`, `src/monitor.ts`,
platform-ops-cli@0880abe `infra/scripts/utils/alerts.py`, `infra/scripts/platform/monitor_health.py`, ops record: prod-baseline-monitoring-backups (2026-11-03)

## Open questions

- `SENTRY_DSN` ตั้งใน Railway ของ service นี้แล้วหรือยัง (ops record บอก Sentry live บน 35 repos แต่ไม่ได้ระบุชื่อ cell นี้)
- ไม่มี dashboard ใดที่พบในไฟล์
