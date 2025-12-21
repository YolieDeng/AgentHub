"""数据库服务"""

from typing import Optional, List
from uuid import UUID
from contextlib import contextmanager

from sqlmodel import SQLModel, Session, create_engine, select
from sqlalchemy.pool import QueuePool

from app.core.config import settings
from app.core.logging import logger
from app.models.user import User
from app.models.session import Session as ChatSession


class DatabaseService:
    """数据库服务类"""

    def __init__(self):
        self._engine = None

    @property
    def engine(self):
        """懒加载数据库引擎"""
        if self._engine is None:
            self._engine = create_engine(
                settings.database_url,
                poolclass=QueuePool,
                pool_size=settings.POSTGRES_POOL_SIZE,
                max_overflow=settings.POSTGRES_MAX_OVERFLOW,
                pool_timeout=30,
                pool_recycle=1800,
                echo=settings.DEBUG,
            )
            logger.info(
                "database_engine_created",
                host=settings.POSTGRES_HOST,
                database=settings.POSTGRES_DB,
            )
        return self._engine

    def create_tables(self):
        """创建所有表"""
        SQLModel.metadata.create_all(self.engine)
        logger.info("database_tables_created")

    @contextmanager
    def get_session(self):
        """获取数据库会话"""
        with Session(self.engine) as session:
            try:
                yield session
                session.commit()
            except Exception as e:
                session.rollback()
                logger.error("database_session_error", error=str(e))
                raise

    # ============ 用户操作 ============

    def create_user(self, email: str, hashed_password: str) -> User:
        """创建用户"""
        with Session(self.engine, expire_on_commit=False) as session:
            user = User(email=email, hashed_password=hashed_password)
            session.add(user)
            session.commit()
            session.refresh(user)
            logger.info("user_created", user_id=str(user.id), email=email)
            return user

    def get_user_by_email(self, email: str) -> Optional[User]:
        """通过邮箱获取用户"""
        with Session(self.engine, expire_on_commit=False) as session:
            statement = select(User).where(User.email == email)
            return session.exec(statement).first()

    def get_user_by_id(self, user_id: UUID) -> Optional[User]:
        """通过 ID 获取用户"""
        with Session(self.engine, expire_on_commit=False) as session:
            return session.get(User, user_id)

    # ============ 会话操作 ============

    def create_chat_session(self, user_id: UUID, title: str = None) -> ChatSession:
        """创建聊天会话"""
        with Session(self.engine, expire_on_commit=False) as session:
            chat_session = ChatSession(user_id=user_id, title=title)
            session.add(chat_session)
            session.commit()
            session.refresh(chat_session)
            logger.info("chat_session_created", session_id=str(chat_session.id))
            return chat_session

    def get_user_sessions(self, user_id: UUID) -> List[ChatSession]:
        """获取用户的所有会话"""
        with Session(self.engine, expire_on_commit=False) as session:
            statement = select(ChatSession).where(ChatSession.user_id == user_id)
            return list(session.exec(statement).all())


# 创建全局数据库服务实例
db = DatabaseService()