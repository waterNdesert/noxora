import asyncio
from getpass import getpass

from email_validator import validate_email
from sqlalchemy import func, select

from src.core.config import settings
from src.core.database import SessionFactory, engine
from src.core.security import hash_password
from src.models.tenant import Tenant
from src.models.user import User


async def provision_initial_admin(email: str, password: str, full_name: str | None) -> None:
    normalized_email = validate_email(email, check_deliverability=False).normalized.lower()
    if not 12 <= len(password) <= 128:
        raise ValueError("Password must contain between 12 and 128 characters")

    async with SessionFactory() as db:
        async with db.begin():
            tenant_result = await db.execute(
                select(Tenant)
                .where(Tenant.id == settings.tenant_id)
                .with_for_update()
            )
            tenant = tenant_result.scalar_one_or_none()
            if tenant is None:
                db.add(Tenant(id=settings.tenant_id, name=settings.tenant_name))

            existing_user_count = await db.scalar(
                select(func.count(User.id)).where(User.tenant_id == settings.tenant_id)
            )
            if existing_user_count:
                raise RuntimeError(
                    "Initial administrator already provisioned; refusing to create another user"
                )

            db.add(
                User(
                    tenant_id=settings.tenant_id,
                    email=normalized_email,
                    hashed_password=hash_password(password),
                    full_name=full_name,
                    role="admin",
                    is_active=True,
                )
            )
    print(f"Initial administrator created for {normalized_email}")


def main() -> None:
    email = input("Administrator email: ").strip()
    full_name = input("Administrator name (optional): ").strip() or None
    password = getpass("Password (12-128 characters): ")
    confirmation = getpass("Confirm password: ")
    if password != confirmation:
        raise ValueError("Passwords do not match")
    async def run() -> None:
        try:
            await provision_initial_admin(email, password, full_name)
        finally:
            await engine.dispose()

    asyncio.run(run())


if __name__ == "__main__":
    main()
