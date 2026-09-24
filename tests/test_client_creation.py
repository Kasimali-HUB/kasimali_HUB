def test_create_client_succeeds(client):
    response = client.post("/api/v1/clients", json={"name": "New Test Client"})
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "New Test Client"
    assert data["country_code"] == "NL"
    assert isinstance(data["id"], int)


def test_created_client_appears_in_the_list(client):
    client.post("/api/v1/clients", json={"name": "Another Client"})
    names = [c["name"] for c in client.get("/api/v1/clients").json()]
    assert "Another Client" in names


def test_create_client_updates_total_client_count(client):
    before = client.get("/api/v1/dashboard/summary").json()["total_client_count"]
    client.post("/api/v1/clients", json={"name": "Count Check Client"})
    after = client.get("/api/v1/dashboard/summary").json()["total_client_count"]
    assert after == before + 1


def test_create_client_rejects_empty_name(client):
    response = client.post("/api/v1/clients", json={"name": "   "})
    assert response.status_code == 422


def test_create_client_rejects_duplicate_name(client):
    client.post("/api/v1/clients", json={"name": "Duplicate Name"})
    response = client.post("/api/v1/clients", json={"name": "Duplicate Name"})
    assert response.status_code == 409


def test_create_client_defaults_country_code_to_nl(client):
    response = client.post("/api/v1/clients", json={"name": "No Country Specified"})
    assert response.json()["country_code"] == "NL"
