"""聊天相关 Schema"""

from typing import Optional

from pydantic import BaseModel


class ChatRequest(BaseModel):
    """聊天请求"""
    message: str
    session_id: Optional[str] = None


class ChatResponse(BaseModel):
    """聊天响应"""
    message: str
    session_id: str


class HistoryResponse(BaseModel):
    """历史响应"""
    session_id: str
    messages: list


class SessionItem(BaseModel):
    """会话项"""
    id: str
    title: Optional[str] = None


class SessionsResponse(BaseModel):
    """会话列表响应"""
    sessions: list[SessionItem]
