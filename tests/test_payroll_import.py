import io

VALID_CSV = (
    b"employee_id,employee_name,annual_gross_salary,actual_net_salary\n"
    b"real-emp-1,Real Employee One,50000,39140.33\n"  # matches engine, not flagged
    b"real-emp-2,Real Employee Two,60000,30000\n"  # way off, should flag
)


def _get_noorderlicht_id(client) -> int:
    clients = client.get("/api/v1/clients").json()
    return next(c["id"] for c in clients if c["name"] == "Noorderlicht B.V.")


def test_import_returns_summary(client):
    client_id = _get_noorderlicht_id(client)
    response = client.post(
        "/api/v1/payroll-runs/import",
        params={"client_id": client_id, "year": 2026, "period": "2026-05"},
        files={"file": ("payroll.csv", io.BytesIO(VALID_CSV), "text/csv")},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["headcount"] == 2
    assert data["total_gross"] == 110_000
    assert data["flagged_count"] == 1


def test_import_updates_the_dashboard(client):
    client_id = _get_noorderlicht_id(client)
    client.post(
        "/api/v1/payroll-runs/import",
        params={"client_id": client_id, "year": 2026, "period": "2026-05"},
        files={"file": ("payroll.csv", io.BytesIO(VALID_CSV), "text/csv")},
    )

    summary = client.get(f"/api/v1/dashboard/summary?client_id={client_id}").json()
    new_period = next(p for p in summary["headcount_series"] if p["period"] == "2026-05")
    assert new_period["value"] == 2

    years = client.get("/api/v1/payroll-runs/years").json()
    assert 2026 in years  # already true, but now backed by a real import too


def test_import_produces_queryable_exceptions_with_no_pii(client):
    client_id = _get_noorderlicht_id(client)
    client.post(
        "/api/v1/payroll-runs/import",
        params={"client_id": client_id, "year": 2026, "period": "2026-05"},
        files={"file": ("payroll.csv", io.BytesIO(VALID_CSV), "text/csv")},
    )

    response = client.get(
        "/api/v1/exceptions",
        params={"client_id": client_id, "year": 2026, "period": "2026-05"},
    )
    assert response.status_code == 200
    payloads = response.json()
    assert len(payloads) == 2
    assert any(p["flagged"] for p in payloads)
    body_text = response.text
    assert "Real Employee" not in body_text
    assert "real-emp" not in body_text  # the raw employee_id shouldn't leak either


def test_reimport_replaces_rather_than_duplicates(client):
    client_id = _get_noorderlicht_id(client)
    for _ in range(2):  # import the same file twice
        client.post(
            "/api/v1/payroll-runs/import",
            params={"client_id": client_id, "year": 2026, "period": "2026-05"},
            files={"file": ("payroll.csv", io.BytesIO(VALID_CSV), "text/csv")},
        )

    summary = client.get(f"/api/v1/dashboard/summary?client_id={client_id}").json()
    period = next(p for p in summary["headcount_series"] if p["period"] == "2026-05")
    assert period["value"] == 2  # not 4

    exceptions = client.get(
        "/api/v1/exceptions",
        params={"client_id": client_id, "year": 2026, "period": "2026-05"},
    ).json()
    assert len(exceptions) == 2  # not 4


def test_import_with_unknown_client_returns_404(client):
    response = client.post(
        "/api/v1/payroll-runs/import",
        params={"client_id": 9999, "year": 2026, "period": "2026-05"},
        files={"file": ("payroll.csv", io.BytesIO(VALID_CSV), "text/csv")},
    )
    assert response.status_code == 404


def test_import_with_bad_csv_returns_422(client):
    client_id = _get_noorderlicht_id(client)
    bad_csv = b"not,the,right,columns\n1,2,3,4\n"
    response = client.post(
        "/api/v1/payroll-runs/import",
        params={"client_id": client_id, "year": 2026, "period": "2026-05"},
        files={"file": ("payroll.csv", io.BytesIO(bad_csv), "text/csv")},
    )
    assert response.status_code == 422


def test_list_payroll_runs_includes_the_new_import(client):
    client_id = _get_noorderlicht_id(client)
    client.post(
        "/api/v1/payroll-runs/import",
        params={"client_id": client_id, "year": 2026, "period": "2026-05"},
        files={"file": ("payroll.csv", io.BytesIO(VALID_CSV), "text/csv")},
    )
    runs = client.get("/api/v1/payroll-runs").json()
    assert any(r["client_id"] == client_id and r["period"] == "2026-05" for r in runs)
