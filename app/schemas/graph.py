"""LangGraph 相关 Schema"""

from typing import List, Literal, Annotated

from pydantic import BaseModel
from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages


class Message(BaseModel):
    """消息模式"""
    role: Literal["user", "assistant", "system"]
    content: str


class GraphState(BaseModel):
    """LangGraph 状态"""
    messages: Annotated[List[BaseMessage], add_messages]
    long_term_memory: str = ""

    class Config:
        arbitrary_types_allowed = True
