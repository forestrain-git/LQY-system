"""
认证API路由 / Authentication API Routes

提供登录、注册等认证相关接口
Provides login, register and other auth endpoints

Author: AI Sprint
Date: 2026-04-08
"""

from datetime import timedelta
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel

from app.core.auth import (
    create_access_token,
    verify_password,
    get_password_hash,
    get_current_user,
    get_current_active_user,
)

router = APIRouter(prefix="/auth", tags=["认证 / Authentication"])

# 模拟用户数据库（生产环境应使用真实数据库）
# Mock user database (production should use real database)
USERS_DB = {
    "admin": {
        "id": 1,
        "username": "admin",
        "hashed_password": get_password_hash("admin123"),
        "role": "admin",
        "is_active": True,
    },
    "operator": {
        "id": 2,
        "username": "operator",
        "hashed_password": get_password_hash("operator123"),
        "role": "operator",
        "is_active": True,
    },
}


class Token(BaseModel):
    """令牌响应模型"""

    access_token: str
    token_type: str = "bearer"
    expires_in: int


class UserInfo(BaseModel):
    """用户信息模型"""

    id: int
    username: str
    role: str


class LoginRequest(BaseModel):
    """登录请求模型"""

    username: str
    password: str


class LoginResponse(BaseModel):
    """登录响应模型"""

    code: int = 0
    message: str = "success"
    data: Token


@router.post("/login", response_model=LoginResponse)
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    """
    用户登录 / User Login

    使用用户名和密码获取访问令牌
    Obtain access token using username and password
    """
    user = USERS_DB.get(form_data.username)

    if not user or not verify_password(form_data.password, user["hashed_password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户名或密码错误",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user.get("is_active", True):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="用户已被禁用",
        )

    access_token_expires = timedelta(days=7)
    access_token = create_access_token(
        data={"sub": str(user["id"]), "username": user["username"], "role": user["role"]},
        expires_delta=access_token_expires,
    )

    return LoginResponse(
        data=Token(
            access_token=access_token,
            token_type="bearer",
            expires_in=604800,  # 7 days in seconds
        )
    )


@router.post("/login/json", response_model=LoginResponse)
async def login_json(credentials: LoginRequest):
    """
    JSON格式登录 / JSON Login

    支持前端直接发送JSON格式的登录请求
    Supports frontend sending JSON format login requests
    """
    user = USERS_DB.get(credentials.username)

    if not user or not verify_password(credentials.password, user["hashed_password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户名或密码错误",
        )

    if not user.get("is_active", True):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="用户已被禁用",
        )

    access_token_expires = timedelta(days=7)
    access_token = create_access_token(
        data={"sub": str(user["id"]), "username": user["username"], "role": user["role"]},
        expires_delta=access_token_expires,
    )

    return LoginResponse(
        data=Token(
            access_token=access_token,
            token_type="bearer",
            expires_in=604800,
        )
    )


@router.get("/me", response_model=dict)
async def get_me(current_user: dict = Depends(get_current_active_user)):
    """
    获取当前用户信息 / Get Current User Info

    需要有效的访问令牌
    Requires valid access token
    """
    return {
        "code": 0,
        "message": "success",
        "data": UserInfo(
            id=current_user["id"],
            username=current_user["username"],
            role=current_user.get("role", "user"),
        ),
    }


@router.post("/logout")
async def logout(current_user: dict = Depends(get_current_user)):
    """
    用户登出 / User Logout

    客户端应删除本地存储的令牌
    Client should delete locally stored token
    """
    # 在实际应用中，这里可以将令牌加入黑名单
    # In real applications, token can be added to blacklist here
    return {"code": 0, "message": "登出成功"}
