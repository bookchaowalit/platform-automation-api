"""Listing, grouping and the lifecycle of cron jobs, rules, pipelines and the run log."""

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


def ids(response):
    assert response.status_code == 200, response.text
    return [item["id"] for item in response.json()["items"]]


def test_cron_jobs_filter_by_job_type_and_status(client, owner):
    backup = create_cron_job(client, owner, name="Backup", job_type="backup").json()
    create_cron_job(client, owner, name="Digest", job_type="digest")
    failed = create_cron_job(
        client, owner, name="Flaky", job_type="backup", last_status="failed"
    ).json()
    by_type = client.get(CRON_JOBS, headers=owner, params={"job_type": "backup"})
    assert ids(by_type) == [backup["id"], failed["id"]]
    by_status = client.get(CRON_JOBS, headers=owner, params={"last_status": "failed"})
    assert ids(by_status) == [failed["id"]]


def test_cron_jobs_filter_by_name_and_active_flag(client, owner):
    wanted = create_cron_job(client, owner, name="Sync calendar").json()
    create_cron_job(client, owner, name="Sync calendar paused", is_active=False)
    by_name = client.get(CRON_JOBS, headers=owner, params={"name": "Sync calendar"})
    assert ids(by_name) == [wanted["id"]]
    inactive = client.get(CRON_JOBS, headers=owner, params={"is_active": "false"})
    assert [i["name"] for i in inactive.json()["items"]] == ["Sync calendar paused"]


def test_a_filter_value_must_parse_as_the_fields_type(client, owner):
    response = client.get(CRON_JOBS, headers=owner, params={"is_active": "yes"})
    assert response.status_code == 422
    assert response.json()["detail"] == {
        "error": "invalid_value",
        "fields": ["is_active"],
    }


def test_listing_by_a_field_that_is_not_a_filter_is_refused(client, owner):
    response = client.get(CRON_JOBS, headers=owner, params={"schedule": "0 2 * * *"})
    assert response.status_code == 422
    assert response.json()["detail"] == {
        "error": "unknown_filter",
        "fields": ["schedule"],
    }


def test_lists_are_ordered_by_id_and_can_be_reversed(client, owner):
    first = create_pipeline(client, owner, name="First").json()
    second = create_pipeline(client, owner, name="Second").json()
    assert ids(client.get(PIPELINES, headers=owner)) == [first["id"], second["id"]]
    newest_first = client.get(PIPELINES, headers=owner, params={"order": "desc"})
    assert ids(newest_first) == [second["id"], first["id"]]


def test_the_log_filters_by_rule_pipeline_and_outcome(client, owner):
    rule = create_rule(client, owner).json()
    pipeline = create_pipeline(client, owner).json()
    by_rule = create_log(client, owner, rule_id=rule["id"]).json()
    by_pipeline = create_log(
        client, owner, pipeline_id=pipeline["id"], action_type="pipeline_run"
    ).json()
    failed = create_log(
        client, owner, success=False, error_message="timeout", action_type="cron_run"
    ).json()
    assert ids(client.get(LOG, headers=owner, params={"rule_id": rule["id"]})) == [
        by_rule["id"]
    ]
    assert ids(
        client.get(LOG, headers=owner, params={"pipeline_id": pipeline["id"]})
    ) == [by_pipeline["id"]]
    assert ids(client.get(LOG, headers=owner, params={"success": "false"})) == [
        failed["id"]
    ]
    assert ids(
        client.get(
            LOG, headers=owner, params={"action_type": ["cron_run", "pipeline_run"]}
        )
    ) == [by_pipeline["id"], failed["id"]]


def test_stats_count_cron_jobs_per_job_type(client, owner):
    create_cron_job(client, owner, name="A", job_type="backup")
    create_cron_job(client, owner, name="B", job_type="backup")
    create_cron_job(client, owner, name="C", job_type="digest")
    stats = client.get(
        f"{CRON_JOBS}/stats", headers=owner, params={"group_by": "job_type"}
    )
    assert stats.status_code == 200, stats.text
    assert stats.json()["groups"] == {"backup": 2, "digest": 1}


def test_stats_count_log_entries_per_action_type(client, owner):
    create_log(client, owner, action_type="rule_fired")
    create_log(client, owner, action_type="rule_fired")
    create_log(client, owner, action_type="cron_run")
    stats = client.get(
        f"{LOG}/stats", headers=owner, params={"group_by": "action_type"}
    )
    assert stats.json()["groups"] == {"rule_fired": 2, "cron_run": 1}


def test_stats_count_rules_per_active_flag(client, owner):
    create_rule(client, owner, name="On")
    create_rule(client, owner, name="Off", is_active=False)
    stats = client.get(
        f"{RULES}/stats", headers=owner, params={"group_by": "is_active"}
    )
    assert stats.status_code == 200, stats.text
    assert sorted(stats.json()["groups"].values()) == [1, 1]


def test_stats_refuse_a_field_that_is_not_a_filter(client, owner):
    for path, field in (
        (CRON_JOBS, "schedule"),
        (RULES, "trigger"),
        (PIPELINES, "steps"),
        (LOG, "description"),
    ):
        stats = client.get(f"{path}/stats", headers=owner, params={"group_by": field})
        assert stats.status_code == 422, path


def test_recording_a_run_bumps_the_version(client, owner):
    job = create_cron_job(client, owner, name="Runs hourly").json()
    path = f"{CRON_JOBS}/{job['id']}"
    ran = client.patch(
        path,
        headers=owner,
        json={
            "last_run_at": "2026-10-22T08:00:00+00:00",
            "next_run_at": "2026-10-22T09:00:00+00:00",
            "last_status": "success",
        },
    )
    assert ran.status_code == 200, ran.text
    assert ran.json()["version"] == 2
    assert ran.json()["last_status"] == "success"
    assert ran.json()["schedule"] == "0 2 * * *"


def test_a_patch_that_changes_nothing_keeps_the_version(client, owner):
    rule = create_rule(client, owner, name="Stable").json()
    same = client.patch(
        f"{RULES}/{rule['id']}",
        headers=owner,
        json={"name": "Stable", "is_active": True},
    )
    assert same.status_code == 200, same.text
    assert same.json()["version"] == 1


def test_a_stale_expected_version_is_refused(client, owner):
    pipeline = create_pipeline(client, owner).json()
    path = f"{PIPELINES}/{pipeline['id']}"
    assert client.patch(path, headers=owner, json={"run_count": 1}).status_code == 200
    stale = client.patch(
        path, headers=owner, json={"run_count": 2, "expected_version": 1}
    )
    assert stale.status_code == 409, stale.text
    assert stale.json()["detail"] == {"error": "version_conflict", "version": 2}


def test_pausing_a_rule_removes_it_from_the_active_list(client, owner):
    rule = create_rule(client, owner, name="Pause me").json()
    paused = client.patch(
        f"{RULES}/{rule['id']}", headers=owner, json={"is_active": False}
    )
    assert paused.status_code == 200, paused.text
    active = client.get(RULES, headers=owner, params={"is_active": "true"})
    assert rule["id"] not in ids(active)


def test_deleting_a_cron_job_removes_it(client, owner):
    job = create_cron_job(client, owner, name="Retired").json()
    path = f"{CRON_JOBS}/{job['id']}"
    assert client.delete(path, headers=owner).status_code == 204
    assert client.get(path, headers=owner).status_code == 404
    assert client.delete(path, headers=owner).status_code == 404


def test_a_rule_can_be_deleted_once_its_log_entries_are_gone(client, owner):
    rule = create_rule(client, owner, name="Short lived").json()
    entry = create_log(client, owner, rule_id=rule["id"]).json()
    assert client.delete(f"{LOG}/{entry['id']}", headers=owner).status_code == 204
    assert client.delete(f"{RULES}/{rule['id']}", headers=owner).status_code == 204
