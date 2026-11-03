# ADR-0002 — Railway serverless service, deployed from GitHub `main` after CI (Wait for CI)

- Status: accepted (retro-documented)
- Date of decision (from history): CD 2026-10-18 (`cc805b3`, `b3f2102`)

## Context

ก่อน 2026-10-18 deploy ด้วย `railway up` จาก working tree (README: "`railway up` is no longer used")

## Decision

- Railway project `platform-automation-api`, service `automation-api`, `sleepApplication: true`, healthcheck `/health` (timeout 60 s)
- Source = GitHub `bookchaowalit/platform-automation-api` branch `main` with `checkSuites: true`; IaC ใน `.railway/railway.ts`, variables unmanaged
- Region Singapore (`asia-southeast1-eqsg3a`) ตั้งด้วย `railway scale` หลัง deploy แรก เพราะ IaC ไม่เก็บ region

## Consequences

- Merge to `main` = production deploy; CI ล้ม = production ค้างที่ deployment ก่อน
- Rollback = redeploy deployment เดิมใน Railway
- Service หลับเมื่อว่าง → request แรกมี cold start; uptime worker probe แบบ hourly

## Evidence

`.railway/railway.ts`, `README.md` (Deploys), `AGENTS.md`, `Dockerfile`, platform-uptime-worker@57f0afb `src/targets.ts` (SLEEPS), GitHub deployments API (env `platform-automation-api / production`)
