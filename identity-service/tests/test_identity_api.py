from __future__ import annotations

from fastapi.testclient import TestClient

from app.main import app


def _admin_headers(client: TestClient) -> dict[str, str]:
    response = client.post(
        "/api/v1/auth/login",
        json={"email": "admin@example.com", "password": "admin123"},
    )
    assert response.status_code == 200
    return {"Authorization": f"Bearer {response.json()['access_token']}"}


def test_health() -> None:
    client = TestClient(app)
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_login_and_me_include_admin_permissions() -> None:
    client = TestClient(app)
    headers = _admin_headers(client)

    response = client.get("/api/v1/auth/me", headers=headers)

    assert response.status_code == 200
    body = response.json()
    assert body["email"] == "admin@example.com"
    assert "platform_admin" in body["roles"]
    assert "identity.users.manage" in body["permissions"]


def test_register_service_permissions_and_assign_branch_scoped_role() -> None:
    client = TestClient(app)
    headers = _admin_headers(client)

    service_response = client.post(
        "/api/v1/services",
        headers=headers,
        json={"code": "converter", "name": "Converter"},
    )
    assert service_response.status_code == 201

    permissions_response = client.post(
        "/api/v1/services/converter/permissions",
        headers=headers,
        json=[
            {"code": "converter.orders.read", "name": "Read converter orders"},
            {"code": "converter.orders.write", "name": "Write converter orders"},
        ],
    )
    assert permissions_response.status_code == 200

    role_response = client.post(
        "/api/v1/roles",
        headers=headers,
        json={
            "code": "converter_operator",
            "name": "Converter Operator",
            "permission_codes": ["converter.orders.read", "converter.orders.write"],
        },
    )
    assert role_response.status_code == 201

    branch_response = client.post(
        "/api/v1/branches",
        headers=headers,
        json={"code": "bishkek", "name": "Bishkek"},
    )
    assert branch_response.status_code == 201

    user_response = client.post(
        "/api/v1/users",
        headers=headers,
        json={
            "email": "operator@example.com",
            "password": "password",
            "full_name": "Operator",
        },
    )
    assert user_response.status_code == 201
    user_id = user_response.json()["id"]

    assignment_response = client.post(
        f"/api/v1/users/{user_id}/role-assignments",
        headers=headers,
        json={"role_code": "converter_operator", "branch_code": "bishkek"},
    )
    assert assignment_response.status_code == 200

    login_response = client.post(
        "/api/v1/auth/login",
        json={"email": "operator@example.com", "password": "password"},
    )
    assert login_response.status_code == 200
    operator_headers = {"Authorization": f"Bearer {login_response.json()['access_token']}"}
    me_response = client.get("/api/v1/auth/me", headers=operator_headers)

    assert me_response.status_code == 200
    body = me_response.json()
    assert body["permissions"] == []
    assert body["branches"] == ["bishkek"]
    assert body["branch_permissions"]["bishkek"] == [
        "converter.orders.read",
        "converter.orders.write",
    ]
