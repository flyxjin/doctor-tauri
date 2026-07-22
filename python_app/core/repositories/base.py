# -*- coding: utf-8 -*-
"""
Repository 基类

提供共享的 db 引用与常用查询辅助方法。
所有 Repository 子类通过 self.db 访问数据库（与 Service 层一致）。

阶段 2.2+：引入 ORM 辅助基础设施，支持子类按需切换到 SQLAlchemy。
  - 只读方法可逐步改用 _session_scope() 走 ORM
  - 写方法仍走 self.db（sqlite3），保持与 Service 层 with self.db.transaction() 的
    跨 Repository 原子性；待阶段 2.4 Database 持有 Engine 后统一切换。
"""
from contextlib import contextmanager
from typing import Any, Dict, List, Optional


class BaseRepository:
    """所有 Repository 的基类，持有 Database 引用。"""

    def __init__(self, db=None):
        # 延迟导入避免循环依赖；db 为 None 时使用单例
        if db is None:
            from core.database import Database
            db = Database()
        self.db = db
        self._session_factory = None

    # ---- SQL 辅助（保留，供写方法与未切换的只读方法使用） ----
    def fetchall(self, query: str, params: tuple = ()) -> List[Dict[str, Any]]:
        return self.db.fetchall(query, params)

    def fetchone(self, query: str, params: tuple = ()) -> Optional[Dict[str, Any]]:
        return self.db.fetchone(query, params)

    def execute(self, query: str, params: tuple = ()):
        return self.db.execute(query, params)

    @contextmanager
    def transaction(self):
        """事务上下文，委托给 Database.transaction()。"""
        with self.db.transaction():
            yield self

    # ---- ORM 辅助（阶段 2.2+ 新增） ----
    @property
    def session_factory(self):
        """懒加载绑定到 self.db.db_path 的 ORM sessionmaker。"""
        if self._session_factory is None:
            from core.db_session import get_session_factory
            self._session_factory = get_session_factory(self.db.db_path)
        return self._session_factory

    @contextmanager
    def _session_scope(self):
        """ORM 会话上下文（独立事务，自动 commit/rollback/close）。

        适用于：
          - 只读查询
          - 独立写操作（不参与 Service 层的 with self.db.transaction()）

        不适用于跨 Repository 复合事务——那类操作仍走 self.db SQL 路径，
        等阶段 2.4 统一切换。
        """
        from core.db_session import session_scope
        with session_scope(self.db.db_path) as session:
            yield session

    @staticmethod
    def _orm_to_dict(orm_obj, extra: Dict[str, Any] = None) -> Dict[str, Any]:
        """将 ORM 对象转为 dict（含所有列），可追加 extra 字段。"""
        if orm_obj is None:
            return None
        result = {c.key: getattr(orm_obj, c.key) for c in orm_obj.__table__.columns}
        if extra:
            result.update(extra)
        return result
