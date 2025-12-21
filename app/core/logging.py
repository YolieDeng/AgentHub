import logging
import sys

import structlog

from app.core.config import settings


def setup_logging():
    """配置结构化日志"""
    log_level = getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO)

    # 确保日志目录存在
    settings.LOG_DIR.mkdir(parents=True, exist_ok=True)

    # 根据格式选择渲染器
    if settings.LOG_FORMAT == "json":
        renderer = structlog.processors.JSONRenderer()
    else:
        renderer = structlog.dev.ConsoleRenderer(colors=True)

    # 配置 structlog
    structlog.configure(
        processors=[
            structlog.contextvars.merge_contextvars,
            structlog.processors.add_log_level,
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            renderer,
        ],
        wrapper_class=structlog.make_filtering_bound_logger(log_level),
        context_class=dict,
        logger_factory=structlog.PrintLoggerFactory(),
        cache_logger_on_first_use=True,
    )

    # 配置标准库日志
    logging.basicConfig(
        format="%(message)s",
        stream=sys.stdout,
        level=log_level,
    )


# 初始化日志
setup_logging()

# 创建全局 logger
logger = structlog.get_logger()