# -*- coding: utf-8 -*-
"""
SQLAlchemy 引擎与会话管理

提供 ORM 层的 Engine 与 Session 工厂：
  - get_engine(db_path): 懒加载单例 Engine（按 db_path 缓存）
  - get_session_factory(db_path): 获取 sessionmaker
  - session_scope(db_path): 上下文管理器，自动提交/回滚/关闭
  - create_worker_session(db_path): 为工作线程创建独立 Session（非单例）

设计要点：
  - SQLite 连接配置与 Database 类保持一致：check_same_thread=False、
    row_factory 由 ORM 接管（不再使用 sqlite3.Row）
  - PRAGMA foreign_keys = ON 在 Engine 的 connect 事件中统一开启，
    确保 ON DELETE CASCADE 在 SQLite 中生效
  - 不在此处调用 Base.metadata.create_all()，表结构由 Database 类管理，
    避免与现有 schema 迁移逻辑冲突
"""
import threading
from contextlib import contextmanager
from typing import Dict, Optional

from sqlalchemy import create_engine, event
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, sessionmaker

# 引擎缓存：db_path -> Engine（单例）
_engines: Dict[str, Engine] = {}
_engines_lock = threading.Lock()


def _build_engine(db_path: str) -> Engine:
    """构造一个 SQLite Engine，启用外键约束。"""
    engine = create_engine(
        f"sqlite:///{db_path}",
        echo=False,
        future=True,
        connect_args={"check_same_thread": False},
    )

    # SQLite 需要显式开启外键约束
    @event.listens_for(engine, "connect")
    def _enable_foreign_keys(dbapi_conn, _):
        cursor = dbapi_conn.cursor()
        cursor.execute("PRAGMA foreign_keys = ON")
        cursor.close()

    return engine


def get_engine(db_path: Optional[str] = None) -> Engine:
    """获取（按 db_path 缓存的）单例 Engine。

    首次调用时创建并缓存，后续相同 db_path 返回同一实例。
    db_path 为 None 时使用默认路径（与 Database.get_db_path() 一致）。
    """
    if db_path is None:
        from core.database import get_db_path
        db_path = get_db_path()

    with _engines_lock:
        if db_path not in _engines:
            _engines[db_path] = _build_engine(db_path)
        return _engines[db_path]


def get_session_factory(db_path: Optional[str] = None) -> sessionmaker:
    """获取绑定到指定 db_path 的 sessionmaker。

    每次调用返回新的 sessionmaker 实例，但底层 Engine 共享单例。
    Repository 可持有 sessionmaker 或每次新建 Session。
    """
    engine = get_engine(db_path)
    return sessionmaker(bind=engine, expire_on_commit=False, class_=Session)


@contextmanager
def session_scope(db_path: Optional[str] = None):
    """事务型会话上下文管理器。

    用法:
        with session_scope() as session:
            session.add(obj)

    - 正常退出自动 commit
    - 异常自动 rollback
    - 始终 close
    """
    factory = get_session_factory(db_path)
    session = factory()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


def create_worker_session(db_path: Optional[str] = None) -> Session:
    """为工作线程创建独立 Session（非单例）。

    调用方负责关闭：
        session = create_worker_session()
        try:
            ...
            session.commit()
        except Exception:
            session.rollback()
        finally:
            session.close()

    底层 Engine 仍为单例（SQLAlchemy Engine 内置连接池，线程安全）。
    """
    factory = get_session_factory(db_path)
    return factory()


def dispose_engine(db_path: Optional[str] = None) -> None:
    """释放并移除指定 db_path 的 Engine（单例重置时调用）。

    db_path 为 None 时释放所有缓存的 Engine。
    主要用于测试 teardown 与应用退出。
    """
    with _engines_lock:
        if db_path is None:
            for eng in _engines.values():
                eng.dispose()
            _engines.clear()
        elif db_path in _engines:
            _engines[db_path].dispose()
            del _engines[db_path]


__all__ = [
    'get_engine', 'get_session_factory', 'session_scope',
    'create_worker_session', 'dispose_engine',
]
