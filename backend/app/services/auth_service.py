from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.user import User
from app.core.security import hash_password, verify_password, create_access_token, create_refresh_token, decode_token


def _format_user_info(user: User) -> dict:
    return {
        "id": user.id,
        "username": user.username,
        "createdAt": user.created_at.isoformat() + "Z" if user.created_at else None,
    }

def _format_user_detail(user: User) -> dict:
    return {
        "id": user.id,
        "username": user.username,
        "createdAt": user.created_at.isoformat() + "Z" if user.created_at else None,
        "updatedAt": user.updated_at.isoformat() + "Z" if user.updated_at else None,
    }

def _generate_auth_response(user: User) -> dict:
    token = create_access_token(user.id)
    refresh_token = create_refresh_token(user.id)
    return {
        "token": token,
        "refreshToken": refresh_token,
        "user": _format_user_info(user)
    }

async def register_user(db: AsyncSession, username: str, password: str) -> dict:
    result = await db.execute(select(User).where(User.username == username))
    existing = result.scalar_one_or_none()
    if existing:
        return None

    user = User(
        username=username,
        hashed_password=hash_password(password)
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)

    return _generate_auth_response(user)

async def authenticate_user(db: AsyncSession, username: str, password: str) -> dict:
    result = await db.execute(select(User).where(User.username == username))
    user = result.scalar_one_or_none()
    if not user:
        return None

    if not verify_password(password, user.hashed_password):
        return None

    if not user.is_active:
        return None

    return _generate_auth_response(user)

async def get_user_by_id(db: AsyncSession, user_id: str) -> dict:
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        return None
    return _format_user_detail(user)

async def refresh_tokens(db: AsyncSession, refresh_token: str) -> dict:
    payload = decode_token(refresh_token)
    if payload is None:
        return None

    if payload.get("type") != "refresh":
        return None

    user_id = payload.get("sub")
    if user_id is None:
        return None

    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        return None

    if not user.is_active:
        return None

    new_token = create_access_token(user.id)
    new_refresh_token = create_refresh_token(user.id)

    return {
        "token": new_token,
        "refreshToken": new_refresh_token
    }
