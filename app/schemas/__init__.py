"""Pydantic 模式定义"""

from typing import List, Optional, Literal, Annotated
from pydantic import BaseModel
from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages


class Message(BaseModel):
    """消息模式"""
    role: Literal["user", "assistant", "system"]
    content: str


class ChatRequest(BaseModel):
    """聊天请求"""
    message: str
    session_id: Optional[str] = None


class ChatResponse(BaseModel):
    """聊天响应"""
    message: str
    session_id: str


class GraphState(BaseModel):
    """LangGraph 状态"""
    messages: Annotated[List[BaseMessage], add_messages]
    long_term_memory: str = ""

    class Config:
        arbitrary_types_allowed = True