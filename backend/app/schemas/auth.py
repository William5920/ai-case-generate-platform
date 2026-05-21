from typing import Optional
from pydantic import BaseModel, Field

class LoginRequest(BaseModel):
    username: str = Field(..., min_length=3, max_length=20)
    password: str = Field(..., min_length=6)

class RegisterRequest(BaseModel):
    username: str = Field(..., min_length=3, max_length=20, pattern=r"^[a-zA-Z0-9_]+$")
    password: str = Field(..., min_length=6)

class RefreshRequest(BaseModel):
    refreshToken: str

class LogoutRequest(BaseModel):
    refreshToken: str

class UserInfo(BaseModel):
    id: str
    username: str
    createdAt: str
    updatedAt: Optional[str] = None

    class Config:
        from_attributes = True

class AuthData(BaseModel):
    token: str
    refreshToken: str
    user: UserInfo

class RefreshData(BaseModel):
    token: str
    refreshToken: str

class ApiResponse(BaseModel):
    code: int = 200
    message: str = "操作成功"
    data: Optional[dict | list | None] = None

def success_response(message: str, data=None) -> dict:
    return {
        "code": 200,
        "message": message,
        "data": data
    }

def error_response(code: int, message: str) -> dict:
    return {
        "code": code,
        "message": message,
        "data": None
    }
