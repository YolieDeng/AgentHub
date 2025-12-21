"""Agent 工具定义"""

from datetime import datetime
from langchain_core.tools import tool


@tool
def get_current_time() -> str:
    """获取当前时间。当用户询问现在几点或需要知道当前时间时使用。"""
    return datetime.now().strftime("%Y年%m月%d日 %H:%M:%S")


@tool
def calculate(expression: str) -> str:
    """计算数学表达式。

    Args:
        expression: 数学表达式，如 "2 + 2" 或 "10 * 5"

    Returns:
        计算结果
    """
    try:
        # 安全地计算表达式（只允许数字和运算符）
        allowed_chars = set("0123456789+-*/().  ")
        if not set(expression).issubset(allowed_chars):
            return "错误：表达式包含不允许的字符"
        result = eval(expression)
        return f"{expression} = {result}"
    except Exception as e:
        return f"计算错误: {str(e)}"


# 工具列表
tools = [
    get_current_time,
    calculate,
]