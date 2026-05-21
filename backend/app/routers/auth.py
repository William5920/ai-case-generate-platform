from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.user import User
from app.schemas.auth import (
    LoginRequest, RegisterRequest, RefreshRequest, LogoutRequest,
    success_response, error_response
)
from app.services import auth_service

router = APIRouter()

@router.post("/register")
async def register(request: RegisterRequest, db: Session = Depends(get_db)):
    result = auth_service.register_user(db, request.username, request.password)
    if result is None:
        return error_response(400, "用户名已存在")
    return success_response("注册成功", result)

@router.post("/login")
async def login(request: LoginRequest, db: Session = Depends(get_db)):
    result = auth_service.authenticate_user(db, request.username, request.password)
    if result is None:
        return error_response(401, "用户名或密码错误")
    return success_response("登录成功", result)

@router.post("/logout")
async def logout(
    request: LogoutRequest,
    current_user: User = Depends(get_current_user)
):
    return success_response("登出成功", None)

@router.get("/user")
async def get_user(current_user: User = Depends(get_current_user)):
    user_info = {
        "id": current_user.id,
        "username": current_user.username,
        "createdAt": current_user.created_at.isoformat() + "Z" if current_user.created_at else None,
        "updatedAt": current_user.updated_at.isoformat() + "Z" if current_user.updated_at else None,
    }
    return success_response("获取成功", user_info)

@router.post("/refresh")
async def refresh_token(request: RefreshRequest, db: Session = Depends(get_db)):
    result = auth_service.refresh_tokens(db, request.refreshToken)
    if result is None:
        return error_response(400, "refreshToken 无效或已过期")
    return success_response("刷新成功", result)
