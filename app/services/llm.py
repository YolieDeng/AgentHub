"""Ollama LLM 服务"""

from typing import List, Optional

from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.messages import BaseMessage
from langchain_ollama import ChatOllama
from tenacity import retry, stop_after_attempt, wait_exponential

from app.core.config import settings
from app.core.logging import logger


class LLMService:
    """LLM 服务类 - 封装 Ollama 模型调用"""

    def __init__(self):
        self._llm: Optional[BaseChatModel] = None
        self._model_name = settings.DEFAULT_LLM_MODEL
        self._initialize()

    def _initialize(self):
        """初始化 LLM"""
        try:
            self._llm = ChatOllama(
                model=self._model_name,
                base_url=settings.OLLAMA_BASE_URL,
                temperature=settings.DEFAULT_LLM_TEMPERATURE,
                num_predict=settings.MAX_TOKENS,
            )
            logger.info(
                "ollama_llm_initialized",
                model=self._model_name,
                base_url=settings.OLLAMA_BASE_URL,
            )
        except Exception as e:
            logger.error("ollama_llm_initialization_failed", error=str(e))
            raise

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        reraise=True,
    )
    async def _call_with_retry(self, messages: List[BaseMessage]) -> BaseMessage:
        """带重试的 LLM 调用"""
        return await self._llm.ainvoke(messages)

    async def call(
        self,
        messages: List[BaseMessage],
        model: Optional[str] = None,
        **kwargs,
    ) -> BaseMessage:
        """调用 LLM

        Args:
            messages: 消息列表
            model: 可选的模型名称
            **kwargs: 其他参数

        Returns:
            LLM 响应消息
        """
        # 如果指定了不同的模型，创建新实例
        if model and model != self._model_name:
            llm = ChatOllama(
                model=model,
                base_url=settings.OLLAMA_BASE_URL,
                temperature=kwargs.get("temperature", settings.DEFAULT_LLM_TEMPERATURE),
                num_predict=kwargs.get("max_tokens", settings.MAX_TOKENS),
            )
            return await llm.ainvoke(messages)

        # 使用默认 LLM
        try:
            response = await self._call_with_retry(messages)
            logger.debug("ollama_call_success", message_count=len(messages))
            return response
        except Exception as e:
            logger.error("ollama_call_failed", error=str(e))
            raise

    def get_llm(self) -> BaseChatModel:
        """获取 LLM 实例"""
        return self._llm

    def bind_tools(self, tools: List) -> "LLMService":
        """绑定工具到 LLM"""
        if self._llm and tools:
            self._llm = self._llm.bind_tools(tools)
            logger.debug("tools_bound_to_llm", count=len(tools))
        return self


# 创建全局 LLM 服务实例
llm_service = LLMService()