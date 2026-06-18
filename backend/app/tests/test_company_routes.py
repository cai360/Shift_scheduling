def test_create_company_requires_auth(api_client):
    resp = api_client.post("/api/companies", json={
        "name": "No Auth Co",
        "description": "Should fail",
    })

    assert resp.status_code == 401


def test_create_company_and_list_my_companies(api_client, login_as):
    _, tokens = login_as()

    create_resp = api_client.post("/api/companies", json={
        "name": "Shift Test Co",
        "description": "API test company",
    }, token=tokens["access_token"])

    assert create_resp.status_code == 201
    company = api_client.data(create_resp)
    assert company["name"] == "Shift Test Co"
    assert company["is_active"] is True

    list_resp = api_client.get("/api/users/me/companies", token=tokens["access_token"])

    assert list_resp.status_code == 200
    companies = api_client.data(list_resp)
    assert companies == [{
        "company_id": company["id"],
        "company_name": "Shift Test Co",
        "role": "owner",
    }]
