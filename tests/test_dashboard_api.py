def test_list_clients_returns_seeded_clients(client):
    response = client.get("/api/v1/clients")
    assert response.status_code == 200
    names = [c["name"] for c in response.json()]
    assert "Noorderlicht B.V." in names
    assert "Delta Logistics NL" in names


def test_dashboard_summary_all_clients_aggregates_across_clients(client):
    response = client.get("/api/v1/dashboard/summary")
    assert response.status_code == 200
    data = response.json()
    assert data["total_client_count"] == 2
    assert data["selected_client_id"] is None
    # 2026-01 headcount should be the sum of both clients' 2026-01 rows (48 + 22)
    jan_2026 = next(p for p in data["headcount_series"] if p["period"] == "2026-01")
    assert jan_2026["value"] == 70


def test_dashboard_summary_filters_by_client(client):
    clients_response = client.get("/api/v1/clients").json()
    target = next(c for c in clients_response if c["name"] == "Noorderlicht B.V.")

    response = client.get(f"/api/v1/dashboard/summary?client_id={target['id']}")
    data = response.json()
    assert data["selected_client_id"] == target["id"]
    # Total client count stays global even when filtering the charts.
    assert data["total_client_count"] == 2
    jan_2026 = next(p for p in data["headcount_series"] if p["period"] == "2026-01")
    assert jan_2026["value"] == 48  # Noorderlicht's own headcount, not summed


def test_available_years_are_distinct_and_sorted_desc(client):
    response = client.get("/api/v1/payroll-runs/years")
    assert response.status_code == 200
    years = response.json()
    assert years == sorted(set(years), reverse=True)
    assert 2026 in years and 2025 in years


def test_exceptions_demo_flags_large_variances_only(client):
    response = client.get("/api/v1/exceptions/demo")
    assert response.status_code == 200
    payloads = response.json()
    flagged = [p for p in payloads if p["flagged"]]
    assert len(flagged) >= 1
    assert len(flagged) < len(payloads)


def test_exceptions_demo_never_leaks_a_name(client):
    response = client.get("/api/v1/exceptions/demo")
    body_text = response.text
    for name_fragment in ["Vries", "Jansen", "Bakker", "Visser"]:
        assert name_fragment not in body_text
