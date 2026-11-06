from collections.abc import Callable
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from app.auth import SESSION_COOKIE

ADMIN = {"email": "Ada@Example.com", "name": "Ada", "password": "correct horse battery"}


def setup_admin(client: TestClient, **overrides: str) -> dict[str, str]:
    response = client.post("/api/setup", json={**ADMIN, **overrides})
    assert response.status_code == 201, response.text
    body: dict[str, str] = response.json()
    return body


def test_fresh_instance_needs_setup(client: TestClient) -> None:
    assert client.get("/api/setup/status").json() == {"needs_setup": True, "token_required": False}


def test_setup_creates_admin_and_signs_in(client: TestClient) -> None:
    member = setup_admin(client)

    assert member["email"] == "ada@example.com"  # normalised
    assert member["role"] == "admin"
    assert client.get("/api/auth/me").json()["id"] == member["id"]
    assert client.get("/api/setup/status").json()["needs_setup"] is False


def test_session_cookie_is_httponly_and_lax(client: TestClient) -> None:
    response = client.post("/api/setup", json=ADMIN)
    cookie = response.headers["set-cookie"]
    assert cookie.startswith(f"{SESSION_COOKIE}=")
    assert "HttpOnly" in cookie
    assert "SameSite=lax" in cookie
    assert "Secure" not in cookie  # public_url is http in tests


def test_setup_only_works_once(client: TestClient) -> None:
    setup_admin(client)
    response = client.post("/api/setup", json={**ADMIN, "email": "eve@example.com"})
    assert response.status_code == 409


def test_concurrent_setups_create_one_admin(make_client: Callable[..., TestClient]) -> None:
    clients = [make_client(), make_client()]
    payloads = [{**ADMIN, "email": f"admin{i}@example.com"} for i in range(2)]
    with ThreadPoolExecutor(max_workers=2) as pool:
        responses = pool.map(lambda c, p: c.post("/api/setup", json=p), clients, payloads)
        codes = sorted(r.status_code for r in responses)
    assert codes == [201, 409]


def test_setup_rejects_short_password(client: TestClient) -> None:
    response = client.post("/api/setup", json={**ADMIN, "password": "short"})
    assert response.status_code == 422


def test_setup_token_is_required_when_configured(make_client: Callable[..., TestClient]) -> None:
    client = make_client(setup_token="s3cret-token")
    assert client.get("/api/setup/status").json()["token_required"] is True
    assert client.post("/api/setup", json=ADMIN).status_code == 403
    assert client.post("/api/setup", json={**ADMIN, "setup_token": "wrong"}).status_code == 403
    response = client.post("/api/setup", json={**ADMIN, "setup_token": "s3cret-token"})
    assert response.status_code == 201


def test_login_and_logout(client: TestClient) -> None:
    setup_admin(client)
    client.cookies.clear()
    assert client.get("/api/auth/me").status_code == 401

    response = client.post(
        "/api/auth/login", json={"email": "ada@example.com", "password": ADMIN["password"]}
    )
    assert response.status_code == 200
    assert client.get("/api/auth/me").status_code == 200

    assert client.post("/api/auth/logout").status_code == 204
    client.cookies.clear()  # the browser drops it on the delete-cookie header
    assert client.get("/api/auth/me").status_code == 401


def test_logged_out_token_cannot_be_reused(client: TestClient) -> None:
    setup_admin(client)
    token = client.cookies[SESSION_COOKIE]
    client.post("/api/auth/logout")
    client.cookies.set(SESSION_COOKIE, token)
    assert client.get("/api/auth/me").status_code == 401


@pytest.mark.parametrize(
    ("email", "password"),
    [("ada@example.com", "wrong password!"), ("nobody@example.com", ADMIN["password"])],
)
def test_login_rejects_bad_credentials(client: TestClient, email: str, password: str) -> None:
    setup_admin(client)
    client.cookies.clear()
    response = client.post("/api/auth/login", json={"email": email, "password": password})
    assert response.status_code == 401
    assert response.json()["detail"] == "Wrong email or password"


def test_cross_origin_post_is_refused(client: TestClient) -> None:
    response = client.post("/api/setup", json=ADMIN, headers={"Origin": "https://evil.example"})
    assert response.status_code == 403
    assert client.get("/api/setup/status").json()["needs_setup"] is True


def test_same_origin_post_is_allowed(client: TestClient) -> None:
    response = client.post("/api/setup", json=ADMIN, headers={"Origin": "http://testserver"})
    assert response.status_code == 201


def test_serves_studio_with_spa_fallback(
    make_client: Callable[..., TestClient], tmp_path: Path
) -> None:
    (tmp_path / "index.html").write_text("<html>studio</html>")
    (tmp_path / "app.js").write_text("console.log(1)")
    client = make_client(studio_dist=tmp_path)
    assert client.get("/").text == "<html>studio</html>"
    assert client.get("/experiences/123").text == "<html>studio</html>"
    assert client.get("/app.js").text == "console.log(1)"
    assert client.get("/api/nope").status_code == 404
    assert client.get("/api/health").json() == {"status": "ok"}
