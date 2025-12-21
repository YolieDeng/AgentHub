"""会话模型"""

from typing import Optional
from uuid import UUID

from sqlmodel import Field

from app.models.base import BaseModel


class Session(BaseModel, table=True):
    """聊天会话表"""
    __tablename__ = "session"

    user_id: UUID = Field(foreign_key="user.id", index=True)
    title: Optional[str] = Field(default=None, max_length=255)