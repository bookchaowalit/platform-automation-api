# SPEC-001 — L2 baseline: locked dependencies, strict types, domain rules under test

Standard: ADR-0004 — TDD + SDD (architecture-docs, `docs/architecture/decisions/ADR-0004-tdd-sdd-standard.md`).
Big Loop Plan Wave 2 (solo-empire `repository-catalog/roadmaps/BIG-LOOP-PLAN-2026-10-21.md`).

## Document control

| Field | Value |
|---|---|
| Spec ID / version | SPEC-001 / 1.0 |
| Status | in review (implemented; owner approval pending) |
| Repository / path | bookchaowalit/platform-automation-api / `specs/001-l2-baseline/spec.md` |
| Owner (maker) | Claude Code (Wave 2 cells session) |
| Reviewer (checker) | Fresh Claude reviewer session (no maker context) |
| Approver | Owner (bookchaowalit): pending, see the Wave 2 report owner actions |
| Requirement links | Big Loop DoD L2: `PRODUCT.md`, ≥ 3 test files, Sentry, type check; L1 lockfile |
| Main-only | yes: committed straight to `main`, so the red run is local (ADR-0004 rule 2, v1.1) |
| Created / approved | 2026-10-22 / pending owner |

## 1. Problem and intent

- **Problem:** Dependencies were installed unpinned, there was no type check, and the only tests were the generic contract suite; nothing tested the automation cell's own rules (required fields, length limits, non-negative counters, log references, imports).
- **Outcome:** the image installs exactly `uv.lock` (`uv sync --frozen`), CI runs Ruff, mypy
  (strict on `src/`) and a coverage gate on shared CI v1.1.1, and the cell's own rules have
  tests of their own beyond the generic contract suite.
- **Why now:** Wave 2 of the Big Loop Plan; milestone M1 is 2026-11-15.

## 2. Scope

| In scope | Out of scope (non-goals) |
|---|---|
| `uv.lock`, Dockerfile, CI caller bump, Ruff/mypy config and fixes, domain tests, `PRODUCT.md` | New endpoints or fields; database migrations; a shared cellkit package (owner decision 2026-10-21: each service owns its code) |

## 3. Behaviour — scenarios

### AC-01 — A cron job needs a name, a schedule and a job type

- **Given** an owner with write permission
- **When** they create a cron job without `name`, `schedule` or `job_type`
- **Then** each create is refused with 422
- **Test:** `tests/test_automation_validation.py::test_a_cron_job_needs_a_name_a_schedule_and_a_job_type` · level: integration (API + throwaway PostgreSQL)

### AC-02 — Retry and run counters cannot be negative

- **Given** an owner with write permission
- **When** they create a cron job with `retry_count` -1
- **Then** the API answers 422; 0 is accepted
- **Test:** `tests/test_automation_validation.py::test_retry_count_cannot_be_negative` · level: integration (API + throwaway PostgreSQL)

### AC-03 — A log entry cannot point at a missing or foreign rule

- **Given** a rule in another workspace
- **When** the owner logs a run with that `rule_id`, or with an id that does not exist
- **Then** the API answers 422 `reference_not_found`
- **Test:** `tests/test_automation_validation.py::test_a_log_entry_cannot_point_at_another_workspaces_rule` · level: integration (API + throwaway PostgreSQL)

### AC-04 — A rule with log entries cannot be deleted

- **Given** a rule with one log entry
- **When** the owner deletes the rule
- **Then** the API answers 409 `has_dependents` and the rule stays
- **Test:** `tests/test_automation_defaults.py::test_a_rule_with_log_entries_cannot_be_deleted` · level: integration (API + throwaway PostgreSQL)

### AC-05 — New cron jobs are active, pending, with no retries

- **Given** a create with only name, schedule and job type
- **When** the job is created
- **Then** `is_active` is true, `last_status` is pending, `retry_count` 0, `params` "{}" and `version` 1
- **Test:** `tests/test_automation_defaults.py::test_new_cron_job_is_active_pending_with_no_retries` · level: integration (API + throwaway PostgreSQL)

### AC-06 — An import keeps its old id and timestamps

- **Given** a cron job sent with `legacy_id` 42 and an old `created_at`
- **When** it is created
- **Then** its id is 42, `created_at` is kept, and it is found at `/v1/cron-jobs/legacy/42`; a repeated import conflicts with 409
- **Test:** `tests/test_automation_defaults.py::test_an_import_keeps_its_old_id_and_timestamps` · level: integration (API + throwaway PostgreSQL)

### AC-07 — Listing and stats follow the declared filters

- **Given** cron jobs of two job types and log entries of two action types
- **When** the owner lists by `job_type` and asks for stats by `job_type`, `action_type` or a non-filter field
- **Then** only matching jobs are listed, stats count per value, and grouping by `schedule` is refused with 422
- **Test:** `tests/test_automation_queries.py::test_stats_count_cron_jobs_per_job_type` · level: integration (API + throwaway PostgreSQL)

### AC-08 — Recording a run bumps the version; an unchanged patch does not

- **Given** a cron job at version 1
- **When** a patch sets `last_run_at`, `next_run_at` and `last_status`, or resends stored values
- **Then** the first is version 2; the unchanged patch keeps the version
- **Test:** `tests/test_automation_queries.py::test_recording_a_run_bumps_the_version` · level: integration (API + throwaway PostgreSQL)

### AC-09 — Numbers fit their columns

- **Given** an int field (PostgreSQL integer) or a real field
- **When** a client sends 2**31, or NaN / Infinity / 1e400 as raw JSON
- **Then** the API answers 422 naming the field (before: a 500 from PostgreSQL, or the value silently stored as null)
- **Test:** `tests/test_contract.py::test_numbers_fit_their_columns` · level: integration (API + throwaway PostgreSQL)

## 4. Interfaces and data

| Interface | Change | Contract |
|---|---|---|
| `/v1/*` (all resources) | unchanged | same routes and payloads; see README |

- **Data model / migration:** N/A — no schema change. Range rules are checked by the API on
  create and update; rows already stored are not rewritten.
- **Backward compatibility:** clients keep the same routes. A write that would store a range
  ending before it starts now gets `422 invalid_value` instead of `201/200`.

## 5. Non-functional requirements

| NFR | Target | How it is tested |
|---|---|---|
| Performance | N/A — no hot-path change beyond one comparison per declared range | — |
| Security / privacy | Same authorization, RLS and Sentry scrubbing as before | contract suite (`tests/test_contract.py`), `tests/test_sentry.py` |
| Reliability / observability | Reproducible image from `uv.lock`; failed inline publishes reach Sentry | image rehearsal before push; `test_inline_publish_failure_is_reported` |
| Accessibility / UX | N/A — API only | — |

## 6. Test plan (TDD)

- **Test levels:** integration tests against the FastAPI app with a throwaway local PostgreSQL
  (pgserver) and a fake platform; no hosted database or platform.
- **Test data:** generated in each test; no production data.
- **Coverage:** CI gate `coverage-threshold: "56"` (measured 58.71% on 2026-10-22, minus 2 points).
- **Not test-first (exceptions):** tests that pin behaviour the service already had
  (characterization tests, marked below) were written after the code by nature; tooling and
  config changes are covered by CI itself.

### Red / green log

| Scenario | Test | Red: commit / run + failure message | Green: commit / run | Refactor note |
|---|---|---|---|---|
| AC-01 | `tests/test_automation_validation.py::test_a_cron_job_needs_a_name_a_schedule_and_a_job_type` | characterization (behaviour already present; passed on first run) | CI run of the pushed tip | none |
| AC-02 | `tests/test_automation_validation.py::test_retry_count_cannot_be_negative` | characterization (behaviour already present; passed on first run) | CI run of the pushed tip | none |
| AC-03 | `tests/test_automation_validation.py::test_a_log_entry_cannot_point_at_another_workspaces_rule` | characterization (behaviour already present; passed on first run) | CI run of the pushed tip | none |
| AC-04 | `tests/test_automation_defaults.py::test_a_rule_with_log_entries_cannot_be_deleted` | characterization (behaviour already present; passed on first run) | CI run of the pushed tip | none |
| AC-05 | `tests/test_automation_defaults.py::test_new_cron_job_is_active_pending_with_no_retries` | characterization (behaviour already present; passed on first run) | CI run of the pushed tip | none |
| AC-06 | `tests/test_automation_defaults.py::test_an_import_keeps_its_old_id_and_timestamps` | characterization (behaviour already present; passed on first run) | CI run of the pushed tip | none |
| AC-07 | `tests/test_automation_queries.py::test_stats_count_cron_jobs_per_job_type` | characterization (behaviour already present; passed on first run) | CI run of the pushed tip | none |
| AC-08 | `tests/test_automation_queries.py::test_recording_a_run_bumps_the_version` | characterization (behaviour already present; passed on first run) | CI run of the pushed tip | none |
| AC-09 | `tests/test_contract.py::test_numbers_fit_their_columns` | e08244b · `.venv/bin/pytest -q -k numbers_fit` · `psycopg.errors.NumericValueOutOfRange: integer out of range` | CI run of the pushed tip | none |

## 7. Risks and open questions

| # | Risk or question | Impact | Owner | Resolution / date |
|---|---|---|---|---|
| 1 | Stored rows written before a range rule existed may already be inverted | a patch touching one of those dates is refused until both are fixed | owner | patches that do not touch the range still work |

## 8. Change log

| Version | Date | Change | Scenarios affected | Approved by |
|---|---|---|---|---|
| 1.0 | 2026-10-22 | Implemented with the Wave 2 baseline | all | pending owner |

## Approval

| Gate | Role | Name / date | Decision | Evidence |
|---|---|---|---|---|
| Implemented (DoD) | Reviewer (checker) | Fresh Claude reviewer / 2026-10-22 | see Wave 2 report | CI run of the pushed tip |
| Implemented (DoD) | Approver | Owner | pending | Wave 2 report |
