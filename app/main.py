"""FastAPI 主应用"""

import importlib
import pkgutil
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.core.logging import logger
from app.services.database import db
import app.api as api_package


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    # 启动时
    logger.info(
        "application_starting",
        project=settings.PROJECT_NAME,
        environment=settings.ENVIRONMENT.value,
    )

    # 创建数据库表
    db.create_tables()

    yield

    # 关闭时
    logger.info("application_shutting_down")


# 创建 FastAPI 应用
app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="FastAPI LangGraph AI Agent with Ollama",
    lifespan=lifespan,
)

# CORS 中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# 健康检查
@app.get("/health")
async def health():
    """健康检查端点"""
    return {
        "status": "healthy",
        "version": settings.VERSION,
        "environment": settings.ENVIRONMENT.value,
    }


# 自动注册路由 - 扫描 app/api/ 下所有模块
for module_info in pkgutil.iter_modules(api_package.__path__):
    module = importlib.import_module(f"app.api.{module_info.name}")
    if hasattr(module, "router"):
        app.include_router(module.router, prefix=settings.API_STR)


# 根路径
@app.get("/")
async def root():
    return {
        "name": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "docs": "/docs",
    }