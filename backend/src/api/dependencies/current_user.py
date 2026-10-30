import hmac
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta

from fastapi import Depends, HTTPException, Request, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.config import settings
from src.core.database import get_db_session
from src.core.security import digest_token
from src.models.session import UserSession
from src.models.user import User

SESSION_IDLE_TIMEOUT = timedelta(minutes=30)
SESSION_ABSOLUTE_LIFETIME = timedelta(hours=12)


def _as_utc(value: datetime) -> datetime:
    if value.tzinfo is None:
        return value.replace(tzinfo=UTC)
    return value.astimezone(UTC)


@dataclass(frozen=True)
class AuthenticatedSession:
    user: User
    session: UserSession


async def get_current_session(
    request: Request,
    db: AsyncSession = Depends(get_db_session),
) -> AuthenticatedSession:
    raw_token = request.cookies.get(settings.session_cookie_name)
    if not raw_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required",
        )

    result = await db.execute(
        select(UserSession)
        .where(
            UserSession.token_digest == digest_token(raw_token),
            UserSession.revoked_at.is_(None),
        )
        .with_for_update()
    )
    user_session = result.scalar_one_or_none()
    if user_session is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required",
        )

    now = datetime.now(UTC)
    idle_expires_at = _as_utc(user_session.idle_expires_at)
    absolute_expires_at = _as_utc(user_session.absolute_expires_at)
    if idle_expires_at <= now or absolute_expires_at <= now:
        user_session.revoked_at = now
        await db.commit()
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Session expired; reauthentication required",
        )

    user = await db.get(User, user_session.user_id)
    if user is None or not user.is_active or user.tenant_id != settings.tenant_id:
        user_session.revoked_at = now
        await db.commit()
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required",
        )

    user_session.last_seen_at = now
    user_session.idle_expires_at = min(
        absolute_expires_at,
        now + SESSION_IDLE_TIMEOUT,
    )
    await db.commit()
    return AuthenticatedSession(user=user, session=user_session)


async def get_current_user(
    authenticated: AuthenticatedSession = Depends(get_current_session),
) -> User:
    return authenticated.user


async def require_csrf_token(
    request: Request,
    authenticated: AuthenticatedSession = Depends(get_current_session),
) -> AuthenticatedSession:
    token = request.headers.get("x-csrf-token")
    if not token or not hmac.compare_digest(
        digest_token(token),
        authenticated.session.csrf_token_digest,
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="A valid CSRF token is required",
        )
    return authenticated
