# 05 — C4 Context

```mermaid
C4Context
  title System Context - Automation cell
  Person(owner, "Owner", "Uses automation-mcp or owner CLI")
  System_Ext(opscli, "platform-ops-cli scripts", "Write run logs, read failed jobs")
  System(cell, "Automation cell", "platform-automation-api: definitions and run log")
  System_Ext(gateway, "Edge API gateway", "gateway.bookchaowalit.com/v1/automation")
  System_Ext(mcphub, "Remote MCP hub", "platform-mcp-remote-worker")
  System_Ext(platform, "empire-platform", "JWKS, authz decide, executions, audit")
  System_Ext(neon, "Neon", "Project platform-automation-api, database automation")
  System_Ext(uptime, "Uptime worker", "Probes /health")
  System_Ext(sentry, "Sentry", "Errors when SENTRY_DSN is set")

  Rel(owner, cell, "MCP tools / HTTPS")
  Rel(opscli, cell, "HTTPS with automation tokens")
  Rel(gateway, cell, "Proxies /v1/automation")
  Rel(mcphub, cell, "Tool calls")
  Rel(cell, platform, "decide, begin, finish, JWKS")
  Rel(cell, neon, "SQL with RLS")
  Rel(uptime, cell, "GET /health")
  Rel(cell, sentry, "Error events")
```

Sources: `README.md`, `PRODUCT.md`, `src/cellkit/platform.py`, `src/cellkit/auth.py`, `src/cellkit/db.py`, `src/cellkit/_sentry.py`, `src/cellkit/mcp.py`,
platform-api-gateway@1f02c2a `routes.json`, platform-mcp-remote-worker@eb10b4d `src/worker.ts` (CELL_HOSTS), platform-uptime-worker@57f0afb `src/targets.ts`,
platform-ops-cli@0880abe `infra/scripts/utils/cell_store.py`, ops record: api-gateway-edge (2026-11-03)

## Open questions

- Gateway ส่งต่อ token ของ caller ตรงไปยัง cell หรือไม่ (cell ตรวจ RS256 เองทุกครั้ง) — ไม่ได้อ่าน gateway code ส่วน forward ใน pack นี้
