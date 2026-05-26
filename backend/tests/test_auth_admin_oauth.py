from __future__ import annotations

import os

import pyotp
import pytest
from fastapi.testclient import TestClient

# Use in-memory auth (no DATABASE_URL)
os.environ.pop("DATABASE_URL", None)

from auth.store import reset_registry, startup  # noqa: E402
from main import create_app  # noqa: E402

ADMIN_EMAIL = "admin@querysafe.io"
ADMIN_PASSWORD = os.getenv("BOOTSTRAP_ADMIN_PASSWORD", "QuerySafe!2026")
EMPLOYEE_PASSWORD = "S3cure!Passw0rd"


@pytest.fixture()
def client():
    reset_registry()
    startup()
    return TestClient(create_app())


def _login_through_2fa(client: TestClient, email: str, password: str) -> dict:
    login = client.post("/auth/login", json={"email": email, "password": password})
    assert login.status_code == 200, login.text
    body = login.json()
    if body.get("approval_pending"):
        pytest.fail("User not approved yet")
    temp_token = body["temp_token"]
    setup = client.post("/auth/setup-2fa", json={"temp_token": temp_token})
    assert setup.status_code == 200, setup.text
    secret = setup.json()["secret"]
    code = pyotp.TOTP(secret).now()
    verify = client.post("/auth/verify-2fa", json={"temp_token": temp_token, "code": code})
    assert verify.status_code == 200, verify.text
    return verify.json()


def test_bootstrap_admin_exists(client: TestClient):
    res = client.post("/auth/login", json={"email": ADMIN_EMAIL, "password": ADMIN_PASSWORD})
    assert res.status_code == 200
    assert res.json().get("temp_token")


def test_register_creates_pending_employee(client: TestClient):
    res = client.post(
        "/auth/register",
        json={
            "email": "employee@test.com",
            "password": EMPLOYEE_PASSWORD,
            "full_name": "Test Employee",
            "department": "finance",
        },
    )
    assert res.status_code == 200
    data = res.json()
    assert data["approval_status"] == "pending"
    assert data["role"] == "viewer"
    assert data["is_active"] is False


def test_pending_employee_cannot_login(client: TestClient):
    client.post(
        "/auth/register",
        json={
            "email": "pending@test.com",
            "password": EMPLOYEE_PASSWORD,
            "full_name": "Pending User",
            "department": "hr",
        },
    )
    res = client.post("/auth/login", json={"email": "pending@test.com", "password": EMPLOYEE_PASSWORD})
    assert res.status_code == 200
    body = res.json()
    assert body.get("approval_pending") is True
    assert body.get("temp_token") is None


def test_admin_approve_and_employee_login(client: TestClient):
    client.post(
        "/auth/register",
        json={
            "email": "approved@test.com",
            "password": EMPLOYEE_PASSWORD,
            "full_name": "Approved User",
            "department": "sales",
        },
    )
    admin_tokens = _login_through_2fa(client, ADMIN_EMAIL, ADMIN_PASSWORD)
    admin_headers = {"Authorization": f"Bearer {admin_tokens['access_token']}"}

    pending = client.get("/admin/users?status_filter=pending", headers=admin_headers)
    assert pending.status_code == 200
    users = pending.json()
    target = next(u for u in users if u["email"] == "approved@test.com")

    approve = client.post(
        f"/admin/users/{target['id']}/approve",
        headers=admin_headers,
        json={"role": "finance", "department": "finance"},
    )
    assert approve.status_code == 200
    approved = approve.json()
    assert approved["approval_status"] == "approved"
    assert approved["role"] == "finance"
    assert approved["is_active"] is True

    emp_tokens = _login_through_2fa(client, "approved@test.com", EMPLOYEE_PASSWORD)
    me = client.get("/auth/me", headers={"Authorization": f"Bearer {emp_tokens['access_token']}"})
    assert me.status_code == 200
    assert me.json()["role"] == "finance"


def test_admin_can_provision_approved_user(client: TestClient):
    admin_tokens = _login_through_2fa(client, ADMIN_EMAIL, ADMIN_PASSWORD)
    admin_headers = {"Authorization": f"Bearer {admin_tokens['access_token']}"}

    created = client.post(
        "/admin/users",
        headers=admin_headers,
        json={
            "email": "provisioned@test.com",
            "password": EMPLOYEE_PASSWORD,
            "full_name": "Provisioned User",
            "department": "engineering",
            "role": "admin",
        },
    )
    assert created.status_code == 201, created.text
    payload = created.json()
    assert payload["approval_status"] == "approved"
    assert payload["is_active"] is True
    assert payload["role"] == "admin"

    login = client.post("/auth/login", json={"email": "provisioned@test.com", "password": EMPLOYEE_PASSWORD})
    assert login.status_code == 200, login.text
    assert login.json().get("temp_token")


def test_non_admin_cannot_list_users(client: TestClient):
    client.post(
        "/auth/register",
        json={
            "email": "regular@test.com",
            "password": EMPLOYEE_PASSWORD,
            "full_name": "Regular",
            "department": "general",
        },
    )
    admin_tokens = _login_through_2fa(client, ADMIN_EMAIL, ADMIN_PASSWORD)
    admin_headers = {"Authorization": f"Bearer {admin_tokens['access_token']}"}
    pending = client.get("/admin/users?status_filter=pending", headers=admin_headers)
    target = next(u for u in pending.json() if u["email"] == "regular@test.com")
    client.post(
        f"/admin/users/{target['id']}/approve",
        headers=admin_headers,
        json={"role": "viewer", "department": "general"},
    )
    emp_tokens = _login_through_2fa(client, "regular@test.com", EMPLOYEE_PASSWORD)
    res = client.get("/admin/users", headers={"Authorization": f"Bearer {emp_tokens['access_token']}"})
    assert res.status_code == 403


def test_admin_reject_user(client: TestClient):
    client.post(
        "/auth/register",
        json={
            "email": "reject@test.com",
            "password": EMPLOYEE_PASSWORD,
            "full_name": "Reject Me",
            "department": "support",
        },
    )
    admin_tokens = _login_through_2fa(client, ADMIN_EMAIL, ADMIN_PASSWORD)
    headers = {"Authorization": f"Bearer {admin_tokens['access_token']}"}
    pending = client.get("/admin/users?status_filter=pending", headers=headers)
    target = next(u for u in pending.json() if u["email"] == "reject@test.com")
    res = client.post(f"/admin/users/{target['id']}/reject", headers=headers)
    assert res.status_code == 200
    assert res.json()["approval_status"] == "rejected"

    login = client.post("/auth/login", json={"email": "reject@test.com", "password": EMPLOYEE_PASSWORD})
    assert login.status_code == 403


def test_oauth_providers_endpoint(client: TestClient):
    res = client.get("/auth/oauth/providers")
    assert res.status_code == 200
    data = res.json()
    assert "google" in data
    assert "github" in data


def test_oauth_google_redirect_without_config(client: TestClient):
    res = client.get("/auth/oauth/google/authorize", follow_redirects=False)
    assert res.status_code == 503


def test_register_blocks_self_admin_role(client: TestClient):
    """Register schema no longer accepts arbitrary admin role."""
    res = client.post(
        "/auth/register",
        json={
            "email": "notadmin@test.com",
            "password": EMPLOYEE_PASSWORD,
            "full_name": "Not Admin",
            "department": "general",
        },
    )
    assert res.status_code == 200
    assert res.json()["role"] == "viewer"
