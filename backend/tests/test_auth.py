from datetime import UTC, datetime, timedelta

import pytest
from sqlalchemy import select

from src.commands import create_initial_admin
from src.core.config import settings
from src.core.security import digest_token, hash_password, verify_password
from src.models.session import UserSession
from src.models.tenant import Tenant
from src.models.user import User

PASSWORD = "correct horse battery staple"
ORIGIN = "http://localhost:8080"


async def add_admin(session_factory) -> User:
    async with session_factory() as db:
        tenant = Tenant(id=settings.tenant_id, name=settings.tenant_name)
        user = User(
            tenant_id=settings.tenant_id,
            email="admin@example.com",
            hashed_password=hash_password(PASSWORD),
            full_name="Nexora Admin",
            role="admin",
            is_active=True,
        )
        db.add_all([tenant, user])
        await db.commit()
        return user


async def test_login_protected_user_and_logout(client, test_session_factory):
    await add_admin(test_session_factory)

    denied = await client.get("/api/users/me")
    assert denied.status_code == 401

    login = await client.post(
        "/api/auth/login",
        headers={"Origin": ORIGIN},
        json={"email": "ADMIN@example.com", "password": PASSWORD},
    )
    assert login.status_code == 200
    assert login.json()["user"]["email"] == "admin@example.com"
    csrf_token = login.json()["csrf_token"]
    cookie = login.cookies.get(settings.session_cookie_name)
    assert cookie
    assert settings.session_cookie_name in login.headers["set-cookie"]
    assert "httponly" in login.headers["set-cookie"].lower()
    assert "samesite=lax" in login.headers["set-cookie"].lower()
    assert "max-age=43200" in login.headers["set-cookie"].lower()
    assert "domain=" not in login.headers["set-cookie"].lower()

    current = await client.get("/api/users/me")
    assert current.status_code == 200
    assert current.json()["email"] == "admin@example.com"
    assert "hashed_password" not in current.json()

    session_digest = digest_token(cookie)
    async with test_session_factory() as db:
        stored_session = await db.scalar(
            select(UserSession).where(UserSession.token_digest == session_digest)
        )
        assert stored_session is not None
        assert stored_session.token_digest != cookie

    logout = await client.post(
        "/api/auth/logout",
        headers={"Origin": ORIGIN, "X-CSRF-Token": csrf_token},
    )
    assert logout.status_code == 204
    assert (await client.get("/api/users/me")).status_code == 401


async def test_login_rejects_bad_credentials_and_untrusted_origin(
    client,
    test_session_factory,
):
    await add_admin(test_session_factory)

    bad_password = await client.post(
        "/api/auth/login",
        headers={"Origin": ORIGIN},
        json={"email": "admin@example.com", "password": "incorrect password value"},
    )
    bad_origin = await client.post(
        "/api/auth/login",
        headers={"Origin": "https://attacker.example"},
        json={"email": "admin@example.com", "password": PASSWORD},
    )

    assert bad_password.status_code == 401
    assert bad_password.json()["detail"] == "Invalid email or password"
    assert bad_origin.status_code == 403


async def test_logout_requires_a_valid_csrf_token(client, test_session_factory):
    await add_admin(test_session_factory)
    await client.post(
        "/api/auth/login",
        headers={"Origin": ORIGIN},
        json={"email": "admin@example.com", "password": PASSWORD},
    )

    response = await client.post(
        "/api/auth/logout",
        headers={"Origin": ORIGIN, "X-CSRF-Token": "invalid"},
    )

    assert response.status_code == 403
    assert (await client.get("/api/users/me")).status_code == 200


async def test_csrf_token_can_be_refreshed_after_a_browser_reload(
    client,
    test_session_factory,
):
    await add_admin(test_session_factory)
    login = await client.post(
        "/api/auth/login",
        headers={"Origin": ORIGIN},
        json={"email": "admin@example.com", "password": PASSWORD},
    )
    initial_token = login.json()["csrf_token"]

    refreshed = await client.get("/api/auth/csrf")
    assert refreshed.status_code == 200
    refreshed_token = refreshed.json()["csrf_token"]
    assert refreshed_token != initial_token

    stale_logout = await client.post(
        "/api/auth/logout",
        headers={"Origin": ORIGIN, "X-CSRF-Token": initial_token},
    )
    valid_logout = await client.post(
        "/api/auth/logout",
        headers={"Origin": ORIGIN, "X-CSRF-Token": refreshed_token},
    )
    assert stale_logout.status_code == 403
    assert valid_logout.status_code == 204


async def test_expired_session_is_revoked(client, test_session_factory):
    await add_admin(test_session_factory)
    login = await client.post(
        "/api/auth/login",
        headers={"Origin": ORIGIN},
        json={"email": "admin@example.com", "password": PASSWORD},
    )
    cookie = login.cookies.get(settings.session_cookie_name)
    assert cookie

    async with test_session_factory() as db:
        stored_session = await db.scalar(
            select(UserSession).where(UserSession.token_digest == digest_token(cookie))
        )
        assert stored_session is not None
        stored_session.idle_expires_at = datetime.now(UTC) - timedelta(seconds=1)
        await db.commit()

    response = await client.get("/api/users/me")
    assert response.status_code == 401

    async with test_session_factory() as db:
        stored_session = await db.scalar(
            select(UserSession).where(UserSession.token_digest == digest_token(cookie))
        )
        assert stored_session is not None
        assert stored_session.revoked_at is not None


async def test_disabled_user_session_is_revoked(client, test_session_factory):
    user = await add_admin(test_session_factory)
    login = await client.post(
        "/api/auth/login",
        headers={"Origin": ORIGIN},
        json={"email": "admin@example.com", "password": PASSWORD},
    )
    cookie = login.cookies.get(settings.session_cookie_name)
    assert cookie

    async with test_session_factory() as db:
        stored_user = await db.get(User, user.id)
        assert stored_user is not None
        stored_user.is_active = False
        await db.commit()

    response = await client.get("/api/users/me")
    assert response.status_code == 401
    async with test_session_factory() as db:
        stored_session = await db.scalar(
            select(UserSession).where(UserSession.token_digest == digest_token(cookie))
        )
        assert stored_session is not None
        assert stored_session.revoked_at is not None


async def test_idle_extension_never_exceeds_absolute_expiry(client, test_session_factory):
    await add_admin(test_session_factory)
    login = await client.post(
        "/api/auth/login",
        headers={"Origin": ORIGIN},
        json={"email": "admin@example.com", "password": PASSWORD},
    )
    cookie = login.cookies.get(settings.session_cookie_name)
    assert cookie
    digest = digest_token(cookie)

    async with test_session_factory() as db:
        stored_session = await db.scalar(
            select(UserSession).where(UserSession.token_digest == digest)
        )
        assert stored_session is not None
        absolute_expiry = datetime.now(UTC) + timedelta(minutes=5)
        stored_session.absolute_expires_at = absolute_expiry
        stored_session.idle_expires_at = datetime.now(UTC) + timedelta(minutes=1)
        await db.commit()

    response = await client.get("/api/users/me")
    assert response.status_code == 200
    async with test_session_factory() as db:
        stored_session = await db.scalar(
            select(UserSession).where(UserSession.token_digest == digest)
        )
        assert stored_session is not None
        stored_absolute_expiry = stored_session.absolute_expires_at.replace(tzinfo=UTC)
        stored_idle_expiry = stored_session.idle_expires_at.replace(tzinfo=UTC)
        assert stored_absolute_expiry == absolute_expiry
        assert stored_idle_expiry <= absolute_expiry


async def test_initial_administrator_provisioning_is_one_time(
    test_session_factory,
    monkeypatch,
):
    monkeypatch.setattr(create_initial_admin, "SessionFactory", test_session_factory)

    await create_initial_admin.provision_initial_admin(
        "first@example.com",
        PASSWORD,
        "First Admin",
    )
    with pytest.raises(RuntimeError, match="already provisioned"):
        await create_initial_admin.provision_initial_admin(
            "second@example.com",
            PASSWORD,
            "Second Admin",
        )

    async with test_session_factory() as db:
        user = await db.scalar(select(User))
        assert user is not None
        assert user.email == "first@example.com"
        assert verify_password(user.hashed_password, PASSWORD)
