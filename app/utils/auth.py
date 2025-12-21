"""JWT 认证工具"""

from datetime import datetime, timedelta
from typing import Optional
from uuid import UUID

from jose import JWTError, jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from app.core.config import settings
from app.core.logging import logger
from app.models.user import User
from app.services.database import db

# Bearer Token 安全方案
security = HTTPBearer()


def create_access_token(user_id: UUID) -> str:
    """创建 JWT 访问令牌"""
    expire = datetime.utcnow() + timedelta(days=settings.JWT_ACCESS_TOKEN_EXPIRE_DAYS)
    payload = {
        "sub": str(user_id),
        "exp": expire,
        "type": "access",
    }
    token = jwt.encode(payload, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)
    return token


def verify_token(token: str) -> Optional[UUID]:
    """验证 JWT 令牌，返回用户 ID"""
    try:
        payload = jwt.decode(
            token,
            settings.JWT_SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM]
        )
        user_id = payload.get("sub")
        if user_id is None:
            return None
        return UUID(user_id)
    except JWTError as e:
        logger.warning("token_verification_failed", error=str(e))
        return None


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> User:
    """获取当前用户（依赖注入）"""
    token = credentials.credentials
    user_id = verify_token(token)

    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="无效的认证令牌",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user = db.get_user_by_id(user_id)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户不存在",
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="用户已被禁用",
        )

    return user