from sqlalchemy.orm import Session
from app.models.user import User
from app.core.security import hash_password, verify_password, create_access_token, create_refresh_token, decode_token
from app.schemas.auth import UserInfo, AuthData, RefreshData

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

def register_user(db: Session, username: str, password: str) -> dict:
    existing = db.query(User).filter(User.username == username).first()
    if existing:
        return None

    user = User(
        username=username,
        hashed_password=hash_password(password)
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    return _generate_auth_response(user)

def authenticate_user(db: Session, username: str, password: str) -> dict:
    user = db.query(User).filter(User.username == username).first()
    if not user:
        return None

    if not verify_password(password, user.hashed_password):
        return None

    if not user.is_active:
        return None

    return _generate_auth_response(user)

def get_user_by_id(db: Session, user_id: str) -> dict:
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        return None
    return _format_user_detail(user)

def refresh_tokens(db: Session, refresh_token: str) -> dict:
    payload = decode_token(refresh_token)
    if payload is None:
        return None

    if payload.get("type") != "refresh":
        return None

    user_id = payload.get("sub")
    if user_id is None:
        return None

    user = db.query(User).filter(User.id == user_id).first()
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
