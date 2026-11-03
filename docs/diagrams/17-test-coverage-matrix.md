# 17 — Test coverage matrix

Test levels ใน repo: **unit** (`tests/test_sentry.py`, `src/cellkit/contract.py::test_spec_refuses_bad_ranges`) และ **integration** (FastAPI TestClient + throwaway PostgreSQL ผ่าน pgserver + fake platform, `src/cellkit/testing.py`, `tests/conftest.py`)
ไม่มี e2e กับ hosted service (AGENTS.md ห้าม). Coverage gate CI 56% (วัดได้ 58.71% วันที่ 2026-10-22)

| Feature | Unit | Integration | E2E | ไฟล์ |
|---|---|---|---|---|
| CRUD lifecycle ทุก resource | — | yes | gap | `contract.py::test_lifecycle` (ผ่าน `tests/test_contract.py`) |
| Validation: required, length, non-negative, types, unknown fields | — | yes | gap | `tests/test_automation_validation.py` (22 tests), `contract.py::test_validation` |
| Numbers fit columns / NaN | — | yes | gap | `contract.py::test_numbers_fit_their_columns` |
| References + has_dependents | — | yes | gap | `test_automation_validation.py`, `test_automation_defaults.py`, `contract.py::test_missing_reference`, `test_no_reference_across_workspaces` |
| Defaults + import legacy_id | — | yes | gap | `tests/test_automation_defaults.py` (11 tests), `contract.py::test_import_keeps_the_old_id` |
| Filters, stats, ordering, versioning | — | yes | gap | `tests/test_automation_queries.py` (16 tests), `contract.py::test_version_conflict` |
| Authorization via platform | — | yes (fake platform) | gap | `contract.py::test_authorization`, `test_executions_are_bound_to_the_record` |
| Workspace isolation (RLS) | — | yes | gap | `contract.py::test_workspace_isolation` |
| Idempotent create | — | yes | gap | `contract.py::test_idempotent_create` |
| JWKS verification | yes | — | gap | `contract.py::test_jwks_verification`, `test_jwks_falls_back_to_the_pinned_key` |
| Outbox publisher | — | yes (whether it runs or skips for this cell: unverified) | gap | `contract.py::test_publisher_delivers_the_outbox`, `test_inline_publish_failure_is_reported` |
| Ranges | yes | inert | — | `contract.py::test_spec_refuses_bad_ranges`, `test_ranges_keep_start_before_end` |
| Sentry scrubbing | yes | — | — | `tests/test_sentry.py` (8 tests) |
| MCP server tools | **gap** | **gap** | **gap** | ไม่มี test ของ `src/cellkit/mcp.py` |
| Importer CLI | **gap** | **gap** | — | ไม่มี test ของ `src/cellkit/importer.py` |
| `automation-db provision` (Neon API) | **gap** | — | — | ไม่มี test |
| Post-deploy `/health` + authorized read | — | — | manual (AGENTS.md) | ไม่มี smoke workflow |

SPEC-001 review (2026-10-24) รายงาน `98 passed, 18 skipped`

Sources: `tests/*.py`, `src/cellkit/contract.py`, `src/cellkit/testing.py`, `.github/workflows/ci.yml`, `specs/001-l2-baseline/spec.md`, `AGENTS.md`, `pyproject.toml`

## Open questions

- 18 skipped tests คือรายการใด (ไม่ได้รัน pytest ใน pack นี้)
