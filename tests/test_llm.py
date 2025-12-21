"""测试 LLM 服务"""

import asyncio
from langchain_core.messages import HumanMessage
from app.services.llm import llm_service


async def test():
    messages = [HumanMessage(content="你好，请用一句话介绍自己")]
    response = await llm_service.call(messages)
    print(f"✅ LLM 回复: {response.content}")


if __name__ == "__main__":
    asyncio.run(test())