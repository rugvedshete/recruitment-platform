from tests.conftest import auth_headers, login_user, register_user


def make_recruiter(client, email="recruiter@example.com"):
    register_user(client, email, role="recruiter")
    return login_user(client, email)


def make_candidate(client, email="candidate@example.com"):
    register_user(client, email, role="candidate")
    return login_user(client, email)


def create_job(client, token, **overrides):
    payload = {
        "title": "Backend Engineer",
        "company": "Acme Corp",
        "description": "Build APIs with FastAPI",
        "location": "Remote",
        "skills": "python,fastapi,postgresql",
        "employment_type": "full_time",
        "salary_min": 80000,
        "salary_max": 120000,
    }
    payload.update(overrides)
    return client.post("/jobs", json=payload, headers=auth_headers(token))


def test_candidate_cannot_create_job(client):
    token = make_candidate(client)
    resp = create_job(client, token)
    assert resp.status_code == 403


def test_recruiter_can_create_job(client):
    token = make_recruiter(client)
    resp = create_job(client, token)
    assert resp.status_code == 201
    assert resp.json()["title"] == "Backend Engineer"


def test_list_jobs_public(client):
    token = make_recruiter(client)
    create_job(client, token)
    resp = client.get("/jobs")
    assert resp.status_code == 200
    body = resp.json()
    assert body["total"] == 1
    assert len(body["items"]) == 1


def test_search_by_query(client):
    token = make_recruiter(client)
    create_job(client, token, title="Backend Engineer", company="Acme")
    create_job(client, token, title="Frontend Engineer", company="Beta Inc")

    resp = client.get("/jobs", params={"q": "Backend"})
    body = resp.json()
    assert body["total"] == 1
    assert body["items"][0]["title"] == "Backend Engineer"


def test_filter_by_location_and_skill(client):
    token = make_recruiter(client)
    create_job(client, token, location="Berlin", skills="python,django")
    create_job(client, token, location="Remote", skills="java,spring")

    resp = client.get("/jobs", params={"location": "Berlin"})
    assert resp.json()["total"] == 1

    resp = client.get("/jobs", params={"skill": "spring"})
    assert resp.json()["total"] == 1
    assert resp.json()["items"][0]["location"] == "Remote"


def test_filter_by_salary_range(client):
    token = make_recruiter(client)
    create_job(client, token, salary_min=50000, salary_max=70000)
    create_job(client, token, salary_min=100000, salary_max=150000)

    resp = client.get("/jobs", params={"min_salary": 90000})
    assert resp.json()["total"] == 1
    assert resp.json()["items"][0]["salary_min"] == 100000


def test_owner_can_update_own_job(client):
    token = make_recruiter(client)
    job = create_job(client, token).json()
    resp = client.put(
        f"/jobs/{job['id']}", json={"title": "Senior Backend Engineer"}, headers=auth_headers(token)
    )
    assert resp.status_code == 200
    assert resp.json()["title"] == "Senior Backend Engineer"


def test_other_recruiter_cannot_edit_job(client):
    token1 = make_recruiter(client, "r1@example.com")
    token2 = make_recruiter(client, "r2@example.com")
    job = create_job(client, token1).json()

    resp = client.put(
        f"/jobs/{job['id']}", json={"title": "Hacked"}, headers=auth_headers(token2)
    )
    assert resp.status_code == 403


def test_delete_job(client):
    token = make_recruiter(client)
    job = create_job(client, token).json()
    resp = client.delete(f"/jobs/{job['id']}", headers=auth_headers(token))
    assert resp.status_code == 204
    assert client.get(f"/jobs/{job['id']}").status_code == 404
