"""Shared helpers for the automation domain tests: paths and minimal valid bodies."""

from typing import Any

CRON_JOBS = "/v1/cron-jobs"
RULES = "/v1/automation-rules"
PIPELINES = "/v1/workflow-pipelines"
LOG = "/v1/automation-log"


def create_cron_job(client: Any, owner: dict[str, str], **fields: Any) -> Any:
    body = {
        "name": "Nightly backup",
        "schedule": "0 2 * * *",
        "job_type": "backup",
        **fields,
    }
    return client.post(CRON_JOBS, headers=owner, json=body)


def create_rule(client: Any, owner: dict[str, str], **fields: Any) -> Any:
    body = {
        "name": "Escalate overdue",
        "trigger": "task.overdue",
        "action": "raise_priority",
        **fields,
    }
    return client.post(RULES, headers=owner, json=body)


def create_pipeline(client: Any, owner: dict[str, str], **fields: Any) -> Any:
    body = {"name": "Publish post", "steps": '["draft", "review", "publish"]', **fields}
    return client.post(PIPELINES, headers=owner, json=body)


def create_log(client: Any, owner: dict[str, str], **fields: Any) -> Any:
    body = {"action_type": "rule_fired", "description": "Raised 2 tasks", **fields}
    return client.post(LOG, headers=owner, json=body)
