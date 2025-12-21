"""LangGraph Agent 工作流"""

import asyncio
from typing import AsyncGenerator, Optional, List
from urllib.parse import quote_plus

from langchain_core.messages import (
    BaseMessage,
    SystemMessage,
    HumanMessage,
    AIMessage,
    ToolMessage,
)
from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver
from langgraph.graph import END, StateGraph
from langgraph.graph.state import Command, CompiledStateGraph
from langgraph.types import RunnableConfig
from psycopg_pool import AsyncConnectionPool

from app.core.config import settings
from app.core.logging import logger
from app.core.langgraph.tools import tools
from app.schemas import GraphState, Message
from app.services.llm import llm_service


# 系统提示词
SYSTEM_PROMPT = """你是一个智能助手。请根据用户的问题提供有帮助的回答。

## 规则
1. 使用中文回答
2. 回答要简洁准确
3. 如果需要，可以使用工具获取信息
4. 如果不确定，诚实地说不知道

## 用户相关记忆
{long_term_memory}
"""


class LangGraphAgent:
    """LangGraph Agent 类"""

    def __init__(self):
        self._connection_pool: Optional[AsyncConnectionPool] = None
        self._graph: Optional[CompiledStateGraph] = None

        # 绑定工具到 LLM
        self.llm_service = llm_service
        self.llm_service.bind_tools(tools)
        self.tools_by_name = {tool.name: tool for tool in tools}

        logger.info("langgraph_agent_initialized")

    async def _get_connection_pool(self) -> AsyncConnectionPool:
        """获取数据库连接池"""
        if self._connection_pool is None:
            connection_url = (
                f"postgresql://{quote_plus(settings.POSTGRES_USER)}:"
                f"{quote_plus(settings.POSTGRES_PASSWORD)}@"
                f"{settings.POSTGRES_HOST}:{settings.POSTGRES_PORT}/"
                f"{settings.POSTGRES_DB}"
            )

            self._connection_pool = AsyncConnectionPool(
                connection_url,
                open=False,
                max_size=settings.POSTGRES_POOL_SIZE,
                kwargs={
                    "autocommit": True,
                    "connect_timeout": 10,
                },
            )
            await self._connection_pool.open()
            logger.info("langgraph_connection_pool_created")

        return self._connection_pool

    async def _chat_node(self, state: GraphState, config: RunnableConfig) -> Command:
        """聊天节点 - 调用 LLM 生成回复"""
        # 构建系统提示词
        system_prompt = SYSTEM_PROMPT.format(
            long_term_memory=state.long_term_memory or "暂无记忆"
        )

        # 构建消息列表
        messages = [SystemMessage(content=system_prompt)] + list(state.messages)

        # 调用 LLM
        response = await self.llm_service.call(messages)

        logger.debug(
            "chat_node_completed",
            has_tool_calls=bool(response.tool_calls) if hasattr(response, 'tool_calls') else False,
        )

        # 判断下一步：有工具调用则去工具节点，否则结束
        if hasattr(response, 'tool_calls') and response.tool_calls:
            return Command(update={"messages": [response]}, goto="tool_node")
        else:
            return Command(update={"messages": [response]}, goto=END)

    async def _tool_node(self, state: GraphState) -> Command:
        """工具节点 - 执行工具调用"""
        outputs = []
        last_message = state.messages[-1]

        for tool_call in last_message.tool_calls:
            tool_name = tool_call["name"]
            tool_args = tool_call["args"]

            logger.info("executing_tool", tool=tool_name, args=tool_args)

            # 执行工具
            tool = self.tools_by_name.get(tool_name)
            if tool:
                result = await tool.ainvoke(tool_args)
            else:
                result = f"未知工具: {tool_name}"

            outputs.append(
                ToolMessage(
                    content=str(result),
                    name=tool_name,
                    tool_call_id=tool_call["id"],
                )
            )

        # 返回聊天节点继续处理
        return Command(update={"messages": outputs}, goto="chat")

    async def create_graph(self) -> CompiledStateGraph:
        """创建并编译 LangGraph"""
        if self._graph is not None:
            return self._graph

        # 构建图
        graph_builder = StateGraph(GraphState)

        # 添加节点
        graph_builder.add_node("chat", self._chat_node)
        graph_builder.add_node("tool_node", self._tool_node)

        # 设置入口和出口
        graph_builder.set_entry_point("chat")
        graph_builder.set_finish_point("chat")

        # 创建检查点保存器（用于持久化对话状态）
        connection_pool = await self._get_connection_pool()
        checkpointer = AsyncPostgresSaver(connection_pool)
        await checkpointer.setup()

        # 编译图
        self._graph = graph_builder.compile(
            checkpointer=checkpointer,
            name=f"{settings.PROJECT_NAME} Agent",
        )

        logger.info("langgraph_compiled")
        return self._graph

    async def chat(
        self,
        message: str,
        session_id: str,
        user_id: Optional[str] = None,
        long_term_memory: str = "",
    ) -> str:
        """发送消息并获取回复"""
        graph = await self.create_graph()

        config = {
            "configurable": {"thread_id": session_id},
            "metadata": {"user_id": user_id},
        }

        # 构建输入
        input_state = {
            "messages": [HumanMessage(content=message)],
            "long_term_memory": long_term_memory,
        }

        # 执行图
        result = await graph.ainvoke(input_state, config)

        # 提取最后一条 AI 消息
        for msg in reversed(result["messages"]):
            if isinstance(msg, AIMessage) and msg.content:
                return msg.content

        return "抱歉，我无法生成回复。"

    async def chat_stream(
        self,
        message: str,
        session_id: str,
        user_id: Optional[str] = None,
        long_term_memory: str = "",
    ) -> AsyncGenerator[str, None]:
        """流式对话"""
        graph = await self.create_graph()

        config = {
            "configurable": {"thread_id": session_id},
            "metadata": {"user_id": user_id},
        }

        input_state = {
            "messages": [HumanMessage(content=message)],
            "long_term_memory": long_term_memory,
        }

        async for token, metadata in graph.astream(
            input_state,
            config,
            stream_mode="messages",
        ):
            if hasattr(token, "content") and token.content:
                yield token.content

    async def get_history(self, session_id: str) -> List[Message]:
        """获取对话历史"""
        graph = await self.create_graph()

        from asgiref.sync import sync_to_async
        state = await sync_to_async(graph.get_state)(
            config={"configurable": {"thread_id": session_id}}
        )

        if not state.values:
            return []

        messages = []
        for msg in state.values.get("messages", []):
            if isinstance(msg, HumanMessage):
                messages.append(Message(role="user", content=msg.content))
            elif isinstance(msg, AIMessage) and msg.content:
                messages.append(Message(role="assistant", content=msg.content))

        return messages

    async def clear_history(self, session_id: str) -> None:
        """清除对话历史"""
        conn_pool = await self._get_connection_pool()
        async with conn_pool.connection() as conn:
            for table in settings.CHECKPOINT_TABLES:
                await conn.execute(
                    f"DELETE FROM {table} WHERE thread_id = %s",
                    (session_id,)
                )
        logger.info("chat_history_cleared", session_id=session_id)


# 创建全局 Agent 实例
agent = LangGraphAgent()