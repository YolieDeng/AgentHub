import os
from enum import Enum
from pathlib import Path
from typing import List

from dotenv import load_dotenv


class Environment(str, Enum):
    """应用环境类型"""
    DEVELOPMENT = "development"
    STAGING = "staging"
    PRODUCTION = "production"
    TEST = "test"


def get_environment() -> Environment:
    """获取当前运行环境"""
    env = os.getenv("APP_ENV", "development").lower()
    match env:
        case "production" | "prod":
            return Environment.PRODUCTION
        case "staging" | "stage":
            return Environment.STAGING
        case "test":
            return Environment.TEST
        case _:
            return Environment.DEVELOPMENT


def load_env_file():
    """加载环境变量文件"""
    env = get_environment()
    base_dir = Path(__file__).parent.parent.parent

    # 按优先级加载 .env 文件
    env_files = [
        base_dir / f".env.{env.value}.local",
        base_dir / f".env.{env.value}",
        base_dir / ".env.local",
        base_dir / ".env",
    ]

    for env_file in env_files:
        if env_file.is_file():
            load_dotenv(dotenv_path=env_file)
            print(f"✅ 已加载配置: {env_file}")
            return env_file

    return None


# 加载环境变量
load_env_file()


def parse_list_from_env(key: str, default: List[str] = None) -> List[str]:
    """解析逗号分隔的环境变量为列表"""
    value = os.getenv(key)
    if not value:
        return default or []
    value = value.strip("\"'")
    if "," not in value:
        return [value]
    return [item.strip() for item in value.split(",") if item.strip()]


class Settings:
    """应用配置类"""

    def __init__(self):
        # 环境
        self.ENVIRONMENT = get_environment()

        # 应用设置
        self.PROJECT_NAME = os.getenv("PROJECT_NAME", "AI Agent")
        self.VERSION = os.getenv("VERSION", "1.0.0")
        self.DEBUG = os.getenv("DEBUG", "false").lower() in ("true", "1", "yes")
        self.API_STR = os.getenv("API_STR", "/api")

        # CORS
        self.ALLOWED_ORIGINS = parse_list_from_env("ALLOWED_ORIGINS", ["*"])

        # Supabase PostgreSQL 数据库配置
        self.POSTGRES_HOST = os.getenv("POSTGRES_HOST", "localhost")
        self.POSTGRES_PORT = int(os.getenv("POSTGRES_PORT", "5432"))
        self.POSTGRES_DB = os.getenv("POSTGRES_DB", "postgres")
        self.POSTGRES_USER = os.getenv("POSTGRES_USER", "postgres")
        self.POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD", "")
        self.POSTGRES_POOL_SIZE = int(os.getenv("POSTGRES_POOL_SIZE", "10"))
        self.POSTGRES_MAX_OVERFLOW = int(os.getenv("POSTGRES_MAX_OVERFLOW", "5"))

        # Ollama 配置
        self.OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
        self.DEFAULT_LLM_MODEL = os.getenv("DEFAULT_LLM_MODEL", "qwen:7b")
        self.DEFAULT_LLM_TEMPERATURE = float(os.getenv("DEFAULT_LLM_TEMPERATURE", "0.7"))
        self.MAX_TOKENS = int(os.getenv("MAX_TOKENS", "4096"))

        # 长期记忆
        self.LONG_TERM_MEMORY_MODEL = os.getenv("LONG_TERM_MEMORY_MODEL", "qwen:7b")
        self.LONG_TERM_MEMORY_EMBEDDER_MODEL = os.getenv(
            "LONG_TERM_MEMORY_EMBEDDER_MODEL", "nomic-embed-text"
        )
        self.LONG_TERM_MEMORY_COLLECTION_NAME = os.getenv(
            "LONG_TERM_MEMORY_COLLECTION_NAME", "longterm_memory"
        )

        # JWT
        self.JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "change-me-in-production")
        self.JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
        self.JWT_ACCESS_TOKEN_EXPIRE_DAYS = int(os.getenv("JWT_ACCESS_TOKEN_EXPIRE_DAYS", "30"))

        # 日志
        self.LOG_DIR = Path(os.getenv("LOG_DIR", "logs"))
        self.LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
        self.LOG_FORMAT = os.getenv("LOG_FORMAT", "console")

        # Checkpoint 表名
        self.CHECKPOINT_TABLES = ["checkpoint_blobs", "checkpoint_writes", "checkpoints"]

    @property
    def database_url(self) -> str:
        """获取数据库连接 URL"""
        return (
            f"postgresql://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}"
            f"@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
        )


# 创建全局配置实例
settings = Settings()