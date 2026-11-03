# ADR-0004 — Authorization, executions and audit delegated to empire-platform with the caller's token (fail closed)

- Status: accepted (retro-documented)
- Date of decision (from history): 2026-10-10; JWKS verification added 2026-10-13 (`30aa274`)

## Decision

- Cell ตรวจ JWT RS256 เอง (audience `automation-api`, issuer `AUTOMATION_JWT_ISSUER`, ต้องมี `exp`, `iat`, `sub`, `jti`, `ws`) ด้วย pinned PEM และ/หรือ JWK Set
- อ่าน: `POST /v1/authz/decide`; เขียน: precheck decide → เปลี่ยนแถวใน transaction → `POST /v1/executions` → commit → `POST /v1/executions/{id}/finish` พร้อม `before_hash` / `after_hash`
- Transport error หรือคำตอบที่ไม่คาด = `PlatformUnavailable` → 503 `authorization_unavailable`

## Consequences

- platform ล่ม = cell อ่าน/เขียนไม่ได้ (product card §6 "fail closed")
- finish ล้มหลัง commit: การเขียนสำเร็จแต่ audit ไม่ครบ → `capture()` ไป Sentry + log `automation.finish_failed`

## Evidence

`src/cellkit/auth.py`, `src/cellkit/platform.py`, `src/cellkit/app.py` (`allow`, `write`), `src/cellkit/contract.py` (`test_authorization`, `test_executions_are_bound_to_the_record`, `test_jwks_verification`), `DOCPACK/00-product-card.md`
