"""Pydantic 模式定义"""

from app.schemas.auth import (
    RegisterRequest,
    LoginRequest,
    TokenResponse,
    UserResponse,
)
from app.schemas.chat import (
    ChatRequest,
    ChatResponse,
    HistoryResponse,
    SessionItem,
    SessionsResponse,
)
from app.schemas.graph import GraphState, Message

__all__ = [
    # Auth
    "RegisterRequest",
    "LoginRequest",
    "TokenResponse",
    "UserResponse",
    # Chat
    "ChatRequest",
    "ChatResponse",
    "HistoryResponse",
    "SessionItem",
    "SessionsResponse",
    # Graph
    "GraphState",
    "Message",
]
