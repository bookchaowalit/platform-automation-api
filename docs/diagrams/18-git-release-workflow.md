# 18 — Git and release workflow

จาก history: งานส่วนใหญ่ผ่าน short-lived branch + PR (#1–#8, 2026-10-17/18) แต่ Wave 2 (2026-10-22) และ SPEC review (2026-10-24) commit ตรงเข้า `main` (SPEC-001: "Main-only: yes")
ไม่มี tag หรือ GitHub release; version ใน `pyproject.toml` คงที่ `0.1.0`

```mermaid
gitGraph
  commit id: "78ad709 cell from kit"
  commit id: "353a8bb rename"
  commit id: "00c7b17 squash PR 1 CI"
  commit id: "4c6c75b squash PR 2 Sentry"
  commit id: "3832c35..d245efc squash PR 3-6"
  branch docs/cd-github-wait-for-ci
  commit id: "cc805b3"
  checkout main
  merge docs/cd-github-wait-for-ci id: "86ab4c9 merge PR 7"
  branch chore/iac-github-source
  commit id: "b3f2102"
  checkout main
  merge chore/iac-github-source id: "ded6e3e merge PR 8"
  commit id: "18c5962 L2 baseline, direct"
  commit id: "8ef9dc1 fix numbers, direct"
  commit id: "06c72b0 SPEC review, direct"
```

PR #1–#6 เป็น squash commit บน `main` (subject ลงท้าย `(#n)`), PR #7–#8 เป็น merge commit ("Merge branch ...")

```mermaid
flowchart LR
  A["Change on branch or main"] --> B["CI api + security"]
  B -- green --> C["merge or push to main"]
  C --> D["Railway Wait for CI"]
  D --> E["deploy automation-api"]
  E --> F["owner verifies /health and one authorized read"]
  F -- broken --> G["redeploy an earlier deployment in Railway"]
```

Sources: `git log origin/main`, `gh pr list -R bookchaowalit/platform-automation-api --state all`, `README.md`, `AGENTS.md`, `specs/001-l2-baseline/spec.md`, `.railway/railway.ts`, `pyproject.toml`
