from tests.conftest import auth_headers, login_user, register_user


def make_recruiter(client, email="recruiter@example.com"):
    register_user(client, email, role="recruiter")
    return login_user(client, email)


def make_candidate(client, email="candidate@example.com"):
    register_user(client, email, role="candidate")
    return login_user(client, email)


def create_job(client, token):
    payload = {
        "title": "Data Engineer",
        "company": "Acme Corp",
        "description": "Build pipelines",
        "location": "Remote",
        "skills": "python,sql,airflow",
    }
    return client.post("/jobs", json=payload, headers=auth_headers(token)).json()


def test_candidate_can_apply(client):
    r_token = make_recruiter(client)
    job = create_job(client, r_token)
    c_token = make_candidate(client)

    resp = client.post(
        "/applications",
        json={"job_id": job["id"], "cover_letter": "I would love to join"},
        headers=auth_headers(c_token),
    )
    assert resp.status_code == 201
    assert resp.json()["status"] == "submitted"


def test_cannot_apply_twice(client):
    r_token = make_recruiter(client)
    job = create_job(client, r_token)
    c_token = make_candidate(client)

    client.post("/applications", json={"job_id": job["id"]}, headers=auth_headers(c_token))
    resp = client.post("/applications", json={"job_id": job["id"]}, headers=auth_headers(c_token))
    assert resp.status_code == 400


def test_recruiter_cannot_apply(client):
    r_token = make_recruiter(client)
    job = create_job(client, r_token)
    resp = client.post("/applications", json={"job_id": job["id"]}, headers=auth_headers(r_token))
    assert resp.status_code == 403


def test_candidate_sees_own_applications(client):
    r_token = make_recruiter(client)
    job = create_job(client, r_token)
    c_token = make_candidate(client)
    client.post("/applications", json={"job_id": job["id"]}, headers=auth_headers(c_token))

    resp = client.get("/applications/me", headers=auth_headers(c_token))
    assert resp.status_code == 200
    assert len(resp.json()) == 1


def test_recruiter_can_view_and_update_applicant_status(client):
    r_token = make_recruiter(client)
    job = create_job(client, r_token)
    c_token = make_candidate(client)
    application = client.post(
        "/applications", json={"job_id": job["id"]}, headers=auth_headers(c_token)
    ).json()

    resp = client.get(f"/applications/job/{job['id']}", headers=auth_headers(r_token))
    assert resp.status_code == 200
    assert len(resp.json()) == 1

    resp = client.put(
        f"/applications/{application['id']}/status",
        json={"status": "interview"},
        headers=auth_headers(r_token),
    )
    assert resp.status_code == 200
    assert resp.json()["status"] == "interview"


def test_other_recruiter_cannot_view_applicants(client):
    r_token1 = make_recruiter(client, "r1@example.com")
    r_token2 = make_recruiter(client, "r2@example.com")
    job = create_job(client, r_token1)
    c_token = make_candidate(client)
    client.post("/applications", json={"job_id": job["id"]}, headers=auth_headers(c_token))

    resp = client.get(f"/applications/job/{job['id']}", headers=auth_headers(r_token2))
    assert resp.status_code == 403
