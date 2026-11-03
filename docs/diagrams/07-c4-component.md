# 07 — C4 Component (automation-api)

`src/solo_automation/` ว่าง (มีแค่ `__init__.py`) และ `cell.yaml` ไม่มี `extend` — ทุก route มาจาก generic `cellkit`

```mermaid
C4Component
  title Components - automation-api
  Container_Ext(caller, "Caller", "token holder")
  ContainerDb_Ext(db, "Neon automation DB")
  System_Ext(platform, "empire-platform")
  System_Ext(sentry, "Sentry")

  Container_Boundary(api, "automation-api") {
    Component(server, "server.py", "entry point", "reads AUTOMATION_* env, builds the app, runs uvicorn")
    Component(spec, "spec.py", "spec loader", "cell.yaml to Cell and Resource")
    Component(app, "app.py", "FastAPI routes", "list, stats, legacy, get, create, patch, delete, /health")
    Component(auth, "auth.py", "TokenVerifier, JwksKeys", "RS256, audience automation-api, channel")
    Component(plat, "platform.py", "HttpPlatform", "decide, begin, finish, publish; fails closed")
    Component(dbm, "db.py", "HostedCluster", "per-role URLs AUTOMATION_DB_URL_*")
    Component(pubm, "publisher.py", "outbox publisher", "inert: no graph resources")
    Component(sen, "_sentry.py", "error reporting", "scrubbed, errors only")
  }

  Rel(caller, app, "HTTPS")
  Rel(server, spec, "load")
  Rel(server, app, "create_app")
  Rel(app, auth, "verify bearer")
  Rel(app, plat, "authz and executions")
  Rel(app, dbm, "connect, set app.workspace_id")
  Rel(app, pubm, "publish_soon, skipped")
  Rel(dbm, db, "psycopg")
  Rel(plat, platform, "httpx")
  Rel(auth, platform, "GET JWKS")
  Rel(sen, sentry, "events")
```

Sources: `src/cellkit/server.py`, `src/cellkit/spec.py`, `src/cellkit/app.py`, `src/cellkit/auth.py`, `src/cellkit/platform.py`, `src/cellkit/db.py`, `src/cellkit/publisher.py`, `src/cellkit/_sentry.py`, `src/solo_automation/__init__.py`, `cell.yaml`

## Open questions

- Production ตั้ง `AUTOMATION_JWT_JWKS_URL` แล้วหรือยัง? README ระบุเฉพาะ `AUTOMATION_JWT_PUBLIC_KEY_PEM` (pinned key) — ถ้าไม่มี JWKS URL, `JwksKeys` จะไม่ถูกใช้
