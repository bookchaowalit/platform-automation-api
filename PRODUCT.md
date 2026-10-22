# Product

<!-- impeccable:product-schema 1 -->

## Platform

api

## Users

- The Solo Empire owner, through the cell's own MCP server (`automation-mcp`, `.mcp.json`).
- Scripts and agents that read and write the automation store through the shared clients listed
  in the registry: `ops-toolkit` (`infra/scripts/utils/cell_store.py`) and `mcp-aggregator`
  (`src/cell-store.ts`, `EMPIRE_AUTOMATION_API`).
- Automations with an `empire-platform` token (for example `owner-mcp`), within the permissions
  `automation.<resource>:read|write|delete`.
- Which cron runner actually reads the job definitions from this cell: [ต้องยืนยัน]

## Product Purpose

One place for the definitions of what runs automatically and a log of what each run did: cron
jobs (what runs and when), task automation rules (trigger → action), workflow pipelines (ordered
steps) and the automation log (each run, the rule or pipeline it ran for, the tasks it touched,
success or error). The cell stores definitions and history; it does not execute jobs itself.

Success: every scheduled job and rule in use is defined here once, and each run leaves a log entry
that names its rule or pipeline.

## Positioning

One capability, one service: its own API (Railway), its own database (Neon) with row-level
security per workspace, and authorization, executions and audit through `empire-platform`. It is
workspace-scoped, so the same service can serve other tenants without code changes.

## Operating Context

- Production: `https://automation-api-production-af8e.up.railway.app` (`/health`), Railway project
  `platform-automation-api`, service `automation-api` (serverless, Singapore next to Neon),
  deployed by merging to `main` after CI.
- Data: Neon project `platform-automation-api`, database `automation`. 26 rows were imported from
  the old SQLite tables keeping their ids (`legacy_id`); new rows get ids from 1,000,000.
- Monitored by `platform-uptime-worker` (`automation-api` target); errors go to Sentry when
  `SENTRY_DSN` is set.

## Capabilities and Constraints

- Every resource has list, stats, get, get-by-legacy-id, create (with `Idempotency-Key`), patch
  (with `expected_version`) and delete:
  - `/v1/cron-jobs` (filters `is_active`, `job_type`, `last_status`, `name`),
  - `/v1/automation-rules` (filter `is_active`),
  - `/v1/workflow-pipelines` (filter `is_active`),
  - `/v1/automation-log` (filters `action_type`, `rule_id`, `pipeline_id`, `success`).
- Rules (covered by `tests/test_automation_*.py`):
  - a cron job needs `name` and `schedule` (1–200 characters) and `job_type` (1–80); `last_status`
    is at most 40 characters and defaults to `pending`; `retry_count` is never negative;
  - a rule needs `trigger` and `action`; `project_filter` and `category_filter` are at most 200
    characters; `execution_count` is never negative;
  - a pipeline needs `steps`; `run_count` is never negative;
  - a log entry needs `action_type` (at most 40) and `description`; `affected_count` is never
    negative; `rule_id` and `pipeline_id` must name a rule or pipeline in the same workspace
    (422 `reference_not_found`), and a rule or pipeline with log entries cannot be deleted
    (409 `has_dependents`);
  - new jobs, rules and pipelines are active by default and log entries count as a success;
  - names are not unique; an import (`legacy_id`) keeps its old id and timestamps, and a repeated
    import conflicts (409); only an import may set `created_at`/`updated_at`;
  - lists are ordered by id (`order=desc` reverses); stats group only by a declared filter; a
    patch that changes nothing keeps the version; a stale `expected_version` is refused (409).
- `params`, `steps` and `affected_tasks` are free text (JSON by convention, not validated);
  `job_type`, `last_status` and `action_type` are free text, not enums. `affected_tasks` holds
  Tasks API ids, which are not checked.
- Out of scope: running jobs, evaluating rules or executing pipelines.

## Measures

Proposed (nothing collects these yet):

- Active cron jobs whose `last_run_at` is older than their schedule allows.
- Share of automation-log entries with `success = false` per week.
- 5xx rate and p95 latency on `/v1/*` (Sentry and uptime worker).
