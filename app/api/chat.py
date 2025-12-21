"""聊天 API"""

import uuid
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from app.core.langgraph.graph import agent
from app.core.logging import logger
from app.models.user import User
from app.utils.auth import get_current_user

router = APIRouter(prefix="/chat", tags=["聊天"])


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


@router.post("", response_model=ChatResponse)
async def chat(
    request: ChatRequest,
    current_user: User = Depends(get_current_user),
):
    """发送消息并获取回复"""
    session_id = request.session_id or str(uuid.uuid4())

    try:
        response = await agent.chat(
            message=request.message,
            session_id=session_id,
            user_id=str(current_user.id),
        )

        logger.info(
            "chat_completed",
            session_id=session_id,
            user_id=str(current_user.id),
        )

        return ChatResponse(message=response, session_id=session_id)

    except Exception as e:
        logger.error("chat_failed", error=str(e))
        raise HTTPException(status_code=500, detail="聊天处理失败")


@router.post("/stream")
async def chat_stream(
    request: ChatRequest,
    current_user: User = Depends(get_current_user),
):
    """流式聊天"""
    session_id = request.session_id or str(uuid.uuid4())

    async def generate():
        try:
            async for token in agent.chat_stream(
                message=request.message,
                session_id=session_id,
                user_id=str(current_user.id),
            ):
                yield f"data: {token}\n\n"
            yield "data: [DONE]\n\n"
        except Exception as e:
            logger.error("stream_failed", error=str(e))
            yield f"data: [ERROR] {str(e)}\n\n"

    return StreamingResponse(
        generate(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Session-ID": session_id,
        },
    )


@router.get("/history/{session_id}", response_model=HistoryResponse)
async def get_history(
    session_id: str,
    current_user: User = Depends(get_current_user),
):
    """获取对话历史"""
    try:
        messages = await agent.get_history(session_id)
        return HistoryResponse(
            session_id=session_id,
            messages=[m.model_dump() for m in messages]
        )
    except Exception as e:
        logger.error("get_history_failed", error=str(e))
        raise HTTPException(status_code=500, detail="获取历史失败")


@router.delete("/history/{session_id}")
async def clear_history(
    session_id: str,
    current_user: User = Depends(get_current_user),
):
    """清除对话历史"""
    try:
        await agent.clear_history(session_id)
        return {"message": "历史已清除"}
    except Exception as e:
        logger.error("clear_history_failed", error=str(e))
        raise HTTPException(status_code=500, detail="清除历史失败")