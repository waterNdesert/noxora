import logging
from datetime import UTC, datetime

from argon2.exceptions import HashingError
from email_validator import EmailNotValidError, validate_email
from fastapi import APIRouter, Depends, HTTPException, Response, status
from pydantic import BaseModel, EmailStr, Field
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.dependencies.current_user import (
    SESSION_ABSOLUTE_LIFETIME,
    SESSION_IDLE_TIMEOUT,
    AuthenticatedSession,
    get_current_session,
    require_csrf_token,
)
from src.core.config import settings
from src.core.database import get_db_session
from src.core.security import (
    digest_token,
    new_csrf_token,
    new_session_token,
    password_hasher,
    verify_password,
)
from src.models.session import UserSession
from src.models.user import User

logger = logging.getLogger(__name__)
router = APIRouter(tags=["authentication"])


class LoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=12, max_length=128)


class UserSummary(BaseModel):
    id: str
    email: str
    full_name: str | None
    role: str


class LoginResponse(BaseModel):
    user: UserSummary
    csrf_token: str


def _user_summary(user: User) -> UserSummary:
    return UserSummary(
        id=str(user.id),
        email=user.email,
        full_name=user.full_name,
        role=user.role,
    )


@router.post("/login", response_model=LoginResponse)
async def login(
    payload: LoginRequest,
    response: Response,
    db: AsyncSession = Depends(get_db_session),
) -> LoginResponse:
    try:
        normalized_email = validate_email(str(payload.email), check_deliverability=False).normalized
    except EmailNotValidError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        ) from None

    result = await db.execute(
        select(User).where(
            User.tenant_id == settings.tenant_id,
            User.email == normalized_email.lower(),
        )
    )
    user = result.scalar_one_or_none()
    if user is None:
        try:
            password_hasher.hash(payload.password)
        except HashingError:
            logger.exception("Password hash operation failed during login")
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Authentication is temporarily unavailable",
            ) from None
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )

    if not verify_password(user.hashed_password, payload.password) or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )

    now = datetime.now(UTC)
    session_token = new_session_token()
    csrf_token = new_csrf_token()
    absolute_expires_at = now + SESSION_ABSOLUTE_LIFETIME
    user_session = UserSession(
        user_id=user.id,
        token_digest=digest_token(session_token),
        csrf_token_digest=digest_token(csrf_token),
        created_at=now,
        last_seen_at=now,
        idle_expires_at=min(now + SESSION_IDLE_TIMEOUT, absolute_expires_at),
        absolute_expires_at=absolute_expires_at,
    )
    db.add(user_session)
    await db.commit()

    response.set_cookie(
        key=settings.session_cookie_name,
        value=session_token,
        max_age=int(SESSION_ABSOLUTE_LIFETIME.total_seconds()),
        httponly=True,
        secure=settings.session_cookie_secure,
        samesite="lax",
        path="/",
    )
    response.headers["Cache-Control"] = "no-store"
    return LoginResponse(user=_user_summary(user), csrf_token=csrf_token)


@router.get("/csrf")
async def rotate_csrf_token(
    response: Response,
    authenticated: AuthenticatedSession = Depends(get_current_session),
    db: AsyncSession = Depends(get_db_session),
) -> dict[str, str]:
    csrf_token = new_csrf_token()
    authenticated.session.csrf_token_digest = digest_token(csrf_token)
    await db.commit()
    response.headers["Cache-Control"] = "no-store"
    return {"csrf_token": csrf_token}


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
async def logout(
    response: Response,
    authenticated: AuthenticatedSession = Depends(require_csrf_token),
    db: AsyncSession = Depends(get_db_session),
) -> None:
    authenticated.session.revoked_at = datetime.now(UTC)
    await db.commit()
    response.delete_cookie(
        key=settings.session_cookie_name,
        path="/",
        secure=settings.session_cookie_secure,
        httponly=True,
        samesite="lax",
    )
    response.headers["Cache-Control"] = "no-store"
