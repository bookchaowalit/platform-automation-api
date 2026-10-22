"""Defaults on create, imports that keep their old id, and what a reference protects."""

from datetime import UTC, datetime

from automation_helpers import (
    CRON_JOBS,
    LOG,
    RULES,
    create_cron_job,
    create_log,
    create_pipeline,
    create_rule,
)


def test_new_cron_job_is_active_pending_with_no_retries(client, owner):
    response = create_cron_job(client, owner)
    assert response.status_code == 201, response.text
    job = response.json()
    assert job["is_active"] is True
    assert job["last_status"] == "pending"
    assert job["retry_count"] == 0
    assert job["params"] == "{}"
    assert job["last_run_at"] is None
    assert job["next_run_at"] is None
    assert job["version"] == 1


def test_new_rule_is_active_and_has_never_run(client, owner):
    rule = create_rule(client, owner).json()
    assert rule["is_active"] is True
    assert rule["execution_count"] == 0
    assert rule["last_executed_at"] is None


def test_new_pipeline_is_active_and_has_never_run(client, owner):
    pipeline = create_pipeline(client, owner).json()
    assert pipeline["is_active"] is True
    assert pipeline["run_count"] == 0
    assert pipeline["steps"] == '["draft", "review", "publish"]'


def test_new_log_entry_counts_as_a_success_with_nothing_affected(client, owner):
    entry = create_log(client, owner).json()
    assert entry["success"] is True
    assert entry["affected_count"] == 0
    assert entry["rule_id"] is None
    assert entry["pipeline_id"] is None


def test_cron_job_names_are_not_unique(client, owner):
    # cell.yaml declares no unique key: two jobs may share a name (e.g. per-region copies).
    assert create_cron_job(client, owner, name="Twin").status_code == 201
    assert create_cron_job(client, owner, name="Twin").status_code == 201


def test_a_log_entry_records_the_rule_and_pipeline_it_ran_for(client, owner):
    rule = create_rule(client, owner).json()
    pipeline = create_pipeline(client, owner).json()
    entry = create_log(
        client,
        owner,
        rule_id=rule["id"],
        pipeline_id=pipeline["id"],
        affected_tasks="[101, 102]",
        affected_count=2,
    )
    assert entry.status_code == 201, entry.text
    assert entry.json()["rule_id"] == rule["id"]
    assert entry.json()["pipeline_id"] == pipeline["id"]


def test_a_rule_with_log_entries_cannot_be_deleted(client, owner):
    rule = create_rule(client, owner, name="Has history").json()
    create_log(client, owner, rule_id=rule["id"])
    refused = client.delete(f"{RULES}/{rule['id']}", headers=owner)
    assert refused.status_code == 409, refused.text
    assert refused.json()["detail"] == {"error": "has_dependents"}
    assert client.get(f"{RULES}/{rule['id']}", headers=owner).status_code == 200


def test_an_import_keeps_its_old_id_and_timestamps(client, owner):
    imported = create_cron_job(
        client,
        owner,
        name="Imported job",
        legacy_id=42,
        created_at="2025-01-02T03:04:05+00:00",
    )
    assert imported.status_code == 201, imported.text
    job = imported.json()
    assert job["id"] == 42
    assert job["legacy_id"] == 42
    assert datetime.fromisoformat(job["created_at"]) == datetime(
        2025, 1, 2, 3, 4, 5, tzinfo=UTC
    )
    by_legacy = client.get(f"{CRON_JOBS}/legacy/42", headers=owner)
    assert by_legacy.status_code == 200, by_legacy.text
    assert by_legacy.json()["name"] == "Imported job"


def test_a_repeated_import_conflicts_instead_of_duplicating(client, owner):
    assert create_log(client, owner, legacy_id=7).status_code == 201
    assert create_log(client, owner, legacy_id=7).status_code == 409


def test_only_an_import_may_set_created_at(client, owner):
    response = create_cron_job(client, owner, created_at="2025-01-02T03:04:05+00:00")
    assert response.status_code == 422, response.text
    assert response.json()["detail"] == {
        "error": "invalid_value",
        "fields": ["created_at"],
    }


def test_new_records_get_ids_above_the_import_range(client, owner):
    entry = create_log(client, owner).json()
    assert entry["id"] >= 1_000_000
    assert client.get(f"{LOG}/{entry['id']}", headers=owner).status_code == 200
