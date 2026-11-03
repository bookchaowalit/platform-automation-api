# 10 — Sequences

## 1. Read: `GET /v1/cron-jobs?last_status=failed`

```mermaid
sequenceDiagram
  autonumber
  participant C as Caller (reporting-reader)
  participant A as automation-api
  participant P as empire-platform
  participant D as Neon automation DB
  C->>A: GET /v1/cron-jobs?last_status=failed, Bearer, X-Empire-Channel
  A->>A: correlate middleware sets X-Correlation-Id
  A->>A: TokenVerifier.verify (RS256, aud automation-api, ws claim)
  alt bad token
    A-->>C: 401 unauthenticated
  end
  A->>P: POST /v1/authz/decide automation.cron-job:read
  alt platform error
    A-->>C: 503 authorization_unavailable
  else deny
    A-->>C: 403 deny
  end
  A->>D: set_config app.workspace_id, SELECT ... WHERE last_status = %s ORDER BY id
  D-->>A: rows of this workspace only (RLS)
  A-->>C: 200 items
```

## 2. Create: `POST /v1/automation-log` (Idempotency-Key)

```mermaid
sequenceDiagram
  autonumber
  participant C as Caller (cron-runner)
  participant A as automation-api
  participant P as empire-platform
  participant D as Neon automation DB
  C->>A: POST /v1/automation-log, Idempotency-Key
  A->>A: verify token, validate body (extra=forbid, limits)
  A->>P: decide automation.automation-log:write on new
  A->>D: BEGIN, reserve id in create_keys, INSERT automation_log
  alt rule_id or pipeline_id not in workspace
    D-->>A: ForeignKeyViolation
    A-->>C: 422 reference_not_found
  end
  A->>P: POST /v1/executions (permission, resource id, idempotency key, correlation id)
  alt replayed and succeeded
    A->>D: ROLLBACK
    A-->>C: existing result
  end
  A->>D: COMMIT
  A->>P: POST /v1/executions/{id}/finish with before_hash and after_hash
  alt finish fails
    A->>A: capture to Sentry, log automation.finish_failed
  end
  A-->>C: 201 record
```

## 3. Update: `PATCH /v1/cron-jobs/{id}` with `expected_version`

```mermaid
sequenceDiagram
  autonumber
  participant C as Caller
  participant A as automation-api
  participant P as empire-platform
  participant D as Neon automation DB
  C->>A: PATCH /v1/cron-jobs/42 expected_version=1
  A->>P: decide automation.cron-job:write on 42
  A->>D: SELECT row FOR UPDATE
  alt version differs
    A-->>C: 409 version_conflict with current version
  end
  alt nothing changed
    A->>P: begin execution, audit verb unchanged
    A->>D: COMMIT, version stays 1
  else fields changed
    A->>D: UPDATE ... version = version + 1, updated_at = now()
    A->>P: begin execution, audit verb updated
    A->>D: COMMIT
  end
  A->>P: POST /v1/executions/{id}/finish
  A-->>C: 200 record
```

## 4. Delete a rule that has log entries

```mermaid
sequenceDiagram
  participant C as Caller
  participant A as automation-api
  participant P as empire-platform
  participant D as Neon automation DB
  C->>A: DELETE /v1/automation-rules/7
  A->>P: decide automation.automation-rule:delete on 7
  A->>D: DELETE FROM automation_rules
  D-->>A: ForeignKeyViolation from automation_log
  A-->>C: 409 has_dependents
```

Sources: `src/cellkit/app.py` (`correlate`, `principal`, `allow`, `write`, `reserve`, `register`), `src/cellkit/auth.py`, `src/cellkit/platform.py`, `migrations/0001_automation.sql`,
`tests/test_automation_defaults.py`, `tests/test_automation_queries.py`, platform-ops-cli@0880abe `infra/scripts/sync/gmail_to_todoist.py`
