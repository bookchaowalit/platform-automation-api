"""What the automation cell refuses: missing or oversize fields, negative counters, bad refs."""

import uuid

from automation_helpers import (
    CRON_JOBS,
    LOG,
    PIPELINES,
    RULES,
    create_cron_job,
    create_log,
    create_pipeline,
    create_rule,
)


def test_a_cron_job_needs_a_name_a_schedule_and_a_job_type(client, owner):
    for missing in ("name", "schedule", "job_type"):
        body = {"name": "Digest", "schedule": "*/5 * * * *", "job_type": "digest"}
        del body[missing]
        response = client.post(CRON_JOBS, headers=owner, json=body)
        assert response.status_code == 422, missing


def test_cron_job_text_fields_cannot_be_empty(client, owner):
    assert create_cron_job(client, owner, name="").status_code == 422
    assert (
        create_cron_job(client, owner, name="Empty schedule", schedule="").status_code
        == 422
    )


def test_cron_job_name_and_schedule_are_limited_to_200_characters(client, owner):
    assert create_cron_job(client, owner, name="n" * 201).status_code == 422
    assert create_cron_job(client, owner, name="n" * 200).status_code == 201
    assert (
        create_cron_job(client, owner, name="Long", schedule="s" * 201).status_code
        == 422
    )


def test_job_type_is_limited_to_80_and_last_status_to_40_characters(client, owner):
    assert create_cron_job(client, owner, job_type="t" * 81).status_code == 422
    assert create_cron_job(client, owner, job_type="t" * 80).status_code == 201
    assert create_cron_job(client, owner, last_status="s" * 41).status_code == 422
    assert create_cron_job(client, owner, last_status="s" * 40).status_code == 201


def test_retry_count_cannot_be_negative(client, owner):
    assert create_cron_job(client, owner, retry_count=-1).status_code == 422
    assert create_cron_job(client, owner, retry_count=0).status_code == 201


def test_is_active_must_be_a_boolean(client, owner):
    assert create_cron_job(client, owner, is_active="sometimes").status_code == 422


def test_next_run_at_must_be_a_timestamp(client, owner):
    assert create_cron_job(client, owner, next_run_at="tomorrow").status_code == 422
    good = create_cron_job(client, owner, next_run_at="2026-10-23T02:00:00+00:00")
    assert good.status_code == 201, good.text


def test_unknown_fields_are_refused(client, owner):
    assert create_cron_job(client, owner, command="rm -rf /").status_code == 422


def test_a_rule_needs_a_trigger_and_an_action(client, owner):
    no_trigger = client.post(
        RULES, headers=owner, json={"name": "No trigger", "action": "notify"}
    )
    assert no_trigger.status_code == 422
    no_action = client.post(
        RULES, headers=owner, json={"name": "No action", "trigger": "task.created"}
    )
    assert no_action.status_code == 422


def test_rule_filters_are_limited_to_200_characters(client, owner):
    assert create_rule(client, owner, project_filter="p" * 201).status_code == 422
    assert create_rule(client, owner, category_filter="c" * 201).status_code == 422
    fits = create_rule(
        client, owner, project_filter="p" * 200, category_filter="c" * 200
    )
    assert fits.status_code == 201, fits.text


def test_rule_execution_count_cannot_be_negative(client, owner):
    assert create_rule(client, owner, execution_count=-1).status_code == 422


def test_priority_filter_must_be_a_whole_number(client, owner):
    assert create_rule(client, owner, priority_filter="high").status_code == 422
    assert create_rule(client, owner, priority_filter=3).status_code == 201


def test_a_pipeline_needs_steps(client, owner):
    response = client.post(PIPELINES, headers=owner, json={"name": "No steps"})
    assert response.status_code == 422
    assert create_pipeline(client, owner, steps="").status_code == 422


def test_pipeline_run_count_cannot_be_negative(client, owner):
    assert create_pipeline(client, owner, run_count=-1).status_code == 422


def test_a_log_entry_needs_an_action_type_and_a_description(client, owner):
    no_type = client.post(LOG, headers=owner, json={"description": "Ran"})
    assert no_type.status_code == 422
    no_description = client.post(LOG, headers=owner, json={"action_type": "ran"})
    assert no_description.status_code == 422


def test_log_action_type_is_limited_to_40_characters(client, owner):
    assert create_log(client, owner, action_type="a" * 41).status_code == 422
    assert create_log(client, owner, action_type="a" * 40).status_code == 201


def test_log_affected_count_cannot_be_negative(client, owner):
    assert create_log(client, owner, affected_count=-1).status_code == 422


def test_a_log_entry_cannot_point_at_a_missing_rule_or_pipeline(client, owner):
    missing_rule = create_log(client, owner, rule_id=999_999_999)
    assert missing_rule.status_code == 422, missing_rule.text
    assert missing_rule.json()["detail"] == {"error": "reference_not_found"}
    missing_pipeline = create_log(client, owner, pipeline_id=999_999_999)
    assert missing_pipeline.status_code == 422, missing_pipeline.text


def test_refs_must_be_positive_ids(client, owner):
    assert create_log(client, owner, rule_id=0).status_code == 422


def test_a_log_entry_cannot_point_at_another_workspaces_rule(
    client, owner, harness, platform
):
    stranger_actor = uuid.uuid4()
    platform.grants[stranger_actor] = set(harness.cell.permissions())
    stranger = harness.token(stranger_actor, uuid.uuid4())
    theirs = create_rule(client, stranger, name="Their rule").json()
    response = create_log(client, owner, rule_id=theirs["id"])
    assert response.status_code == 422, response.text


def test_patching_a_log_entry_to_a_missing_pipeline_is_refused(client, owner):
    entry = create_log(client, owner).json()
    path = f"{LOG}/{entry['id']}"
    refused = client.patch(path, headers=owner, json={"pipeline_id": 999_999_999})
    assert refused.status_code == 422, refused.text
    assert client.get(path, headers=owner).json()["pipeline_id"] is None


def test_required_fields_cannot_be_cleared_by_a_patch(client, owner):
    job = create_cron_job(client, owner, name="Keep schedule").json()
    cleared = client.patch(
        f"{CRON_JOBS}/{job['id']}", headers=owner, json={"schedule": None}
    )
    assert cleared.status_code == 422, cleared.text
    assert cleared.json()["detail"] == {
        "error": "invalid_value",
        "fields": ["schedule"],
    }
