"""
JWT认证模块 / JWT Authentication Module

提供JWT令牌生成和验证功能
Provides JWT token generation and verification

Author: AI Sprint
Date: 2026-04-08
"""

from datetime import datetime, timedelta, timezone
from typing import Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt
from passlib.context import CryptContext

# JWT配置 / JWT Configuration
SECRET_KEY = "lqy-sprint-secret-key-2026-change-in-production"  # 生产环境必须更改
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_DAYS = 7

# 密码加密上下文 / Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# HTTP Bearer安全方案
security = HTTPBearer()


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    验证密码 / Verify password

    Args:
        plain_password: 明文密码 / Plain text password
        hashed_password: 哈希密码 / Hashed password

    Returns:
        bool: 是否匹配 / Whether passwords match
    """
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """
    获取密码哈希 / Get password hash

    Args:
        password: 明文密码 / Plain text password

    Returns:
        str: 哈希密码 / Hashed password
    """
    return pwd_context.hash(password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    创建访问令牌 / Create access token

    Args:
        data: 要编码的数据 / Data to encode
        expires_delta: 过期时间增量 / Expiration time delta

    Returns:
        str: JWT令牌 / JWT token
    """
    to_encode = data.copy()

    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(days=ACCESS_TOKEN_EXPIRE_DAYS)

    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

    return encoded_jwt


def verify_token(token: str) -> Optional[dict]:
    """
    验证令牌 / Verify token

    Args:
        token: JWT令牌 / JWT token

    Returns:
        dict or None: 解码后的数据 / Decoded data
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        return None


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> dict:
    """
    获取当前用户 / Get current user

    依赖项，用于保护API端点
    Dependency for protecting API endpoints

    Args:
        credentials: HTTP认证凭据 / HTTP authorization credentials

    Returns:
        dict: 用户信息 / User info

    Raises:
        HTTPException: 401 如果认证失败
    """
    token = credentials.credentials
    payload = verify_token(token)

    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="无效的认证凭据",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user_id: str = payload.get("sub")
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="无效的认证凭据",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return {"id": user_id, "username": payload.get("username")}


async def get_current_active_user(
    current_user: dict = Depends(get_current_user)
) -> dict:
    """
    获取当前活跃用户 / Get current active user

    Args:
        current_user: 当前用户信息 / Current user info

    Returns:
        dict: 用户信息 / User info

    Raises:
        HTTPException: 403 如果用户被禁用
    """
    # 这里可以添加用户状态检查
    # 例如：检查用户是否被禁用
    return current_user
