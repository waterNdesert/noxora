from fastapi import APIRouter, Depends, Response
from pydantic import BaseModel

from src.api.dependencies.current_user import get_current_user
from src.models.user import User

router = APIRouter(tags=["users"])


class CurrentUserResponse(BaseModel):
    id: str
    email: str
    full_name: str | None
    role: str


@router.get("/me", response_model=CurrentUserResponse)
async def current_user(
    response: Response,
    user: User = Depends(get_current_user),
) -> CurrentUserResponse:
    response.headers["Cache-Control"] = "no-store"
    return CurrentUserResponse(
        id=str(user.id),
        email=user.email,
        full_name=user.full_name,
        role=user.role,
    )
