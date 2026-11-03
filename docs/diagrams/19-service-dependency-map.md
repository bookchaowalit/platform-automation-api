# 19 — Service dependency map

```mermaid
flowchart TB
  subgraph Up["Upstream: callers of this cell"]
    OPS["platform-ops-cli scripts: gmail_to_todoist, gmail_categorizer, gmail_daily_digest, monitor_health, decision_engine, alerts, cell_probe"]
    AGG["platform-mcp-aggregator cell-store.ts"]
    HUB["platform-mcp-remote-worker"]
    GW["platform-api-gateway"]
    MCP["automation-mcp, owner machine"]
    UPT["platform-uptime-worker"]
  end
  API["automation-api"]
  subgraph Down["Downstream: what this cell needs at runtime"]
    EP["empire-platform: /v1/authz/decide, /v1/executions, JWKS"]
    NEON[("Neon platform-automation-api")]
    SEN["Sentry, optional"]
  end
  subgraph Build["Build and deploy time"]
    GHA["GitHub Actions + platform-ci-workflows v1.1.1"]
    RWY["Railway"]
    NAPI["Neon API, provision only"]
  end
  OPS --> API
  AGG --> API
  HUB --> API
  GW --> API
  MCP --> API
  UPT --> API
  API -- "hard: fail closed 503" --> EP
  API -- "hard: 503 unavailable" --> NEON
  API -. "soft" .-> SEN
  GHA --> RWY
  RWY --> API
  NAPI -.-> NEON
```

| Dependency | Type | ถ้าล่ม |
|---|---|---|
| empire-platform | hard, sync HTTP ทุก request ที่มี token | 503 `authorization_unavailable` (อ่านและเขียนไม่ได้) |
| Neon | hard | 503 `unavailable` (connect timeout 15 s) |
| JWKS endpoint | soft (cache + pinned PEM fallback) | ใช้ key เดิม |
| Sentry | soft | ไม่มีผลต่อ request |
| Tasks API | none (เก็บ id ใน `affected_tasks` ไม่เรียก) | — |

Sources: `src/cellkit/platform.py`, `src/cellkit/auth.py`, `src/cellkit/db.py`, `src/cellkit/app.py`, `src/cellkit/_sentry.py`, `.github/workflows/ci.yml`, `.railway/railway.ts`, `PRODUCT.md`,
platform-ops-cli@0880abe `infra/scripts/**` (ไฟล์ตามชื่อใน diagram), platform-mcp-remote-worker@eb10b4d `src/worker.ts`, platform-api-gateway@1f02c2a `routes.json`, platform-uptime-worker@57f0afb `src/targets.ts`,
solo-empire `repository-catalog/registries/online-systems.yaml` (`automation`, `client` field)
