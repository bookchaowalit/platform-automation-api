# 06 — C4 Container

Image เดียว (`Dockerfile`, CMD `automation-api`) แต่ `pyproject.toml` ประกาศ entry points 4 ตัว: `automation-api`, `automation-publish`, `automation-db`, `automation-mcp`
บน Railway มี service เดียวคือ `automation-api` (`.railway/railway.ts`) — ไม่มี publisher cron service

```mermaid
C4Container
  title Containers - Automation cell
  Person(owner, "Owner / agent")
  System_Ext(opscli, "platform-ops-cli scripts")
  System_Ext(platform, "empire-platform")

  System_Boundary(c, "platform-automation-api") {
    Container(api, "automation-api", "Python 3.13, FastAPI, uvicorn", "Railway serverless, Singapore")
    Container(mcp, "automation-mcp", "Python, MCP stdio", "Runs on the owner machine, calls the API")
    Container(dbcli, "automation-db", "Python CLI", "migrate / provision, run by the owner")
    Container(pub, "automation-publish", "Python CLI", "Outbox sweep; not deployed")
    ContainerDb(db, "automation database", "Neon PostgreSQL", "schema automation, RLS per workspace")
  }

  Rel(owner, mcp, "stdio")
  Rel(mcp, api, "HTTPS bearer")
  Rel(opscli, api, "HTTPS bearer")
  Rel(api, db, "role automation_api")
  Rel(api, platform, "HTTPS, caller token")
  Rel(dbcli, db, "role automation_migrator")
  Rel(pub, db, "role automation_publisher")
  Rel(pub, platform, "POST /v1/graph/events")
```

Sources: `Dockerfile`, `pyproject.toml` (`[project.scripts]`), `.railway/railway.ts`, `.mcp.json`, `src/cellkit/server.py`, `src/cellkit/db.py`, `src/cellkit/publisher.py`, `db/roles.sql`, `migrations/0001_automation.sql`

## Open questions

- `automation-publish` ไม่มีที่รัน และไม่มี resource ใดประกาศ `graph` ใน `cell.yaml` จึงไม่มี outbox row — จะลบออกหรือคงไว้เป็น inert code (`docs/cellkit-notes.md` บอกว่า inert)
