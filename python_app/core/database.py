# -*- coding: utf-8 -*-
"""
数据层 - 数据库连接和基础操作

阶段 2.4：Database 持有 SQLAlchemy Engine，表结构改由 ORM metadata 管理。
  - 表创建：Base.metadata.create_all(engine) 替代手写 CREATE TABLE
  - 索引创建：仍用手写 SQL（ORM 未显式定义这些辅助索引）
  - Schema 迁移：保留 _migrate_schema（create_all 不修改已存在的表）
  - sqlite3 连接：保留作为写方法过渡路径（与 Service 层 with self.db.transaction() 兼容）
  - 新增 session_scope()：供 Repository 只读方法走 ORM
"""
import os
import shutil
import sqlite3
import sys
import threading
from contextlib import contextmanager
from datetime import datetime
from typing import Any, Dict, List, Optional


def get_app_data_dir() -> str:
    if getattr(sys, 'frozen', False):
        app_data = os.environ.get('APPDATA', os.path.expanduser('~'))
        app_dir = os.path.join(app_data, 'MedicineSystem')
    else:
        app_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    if not os.path.exists(app_dir):
        os.makedirs(app_dir)

    return app_dir


def get_db_path() -> str:
    app_dir = get_app_data_dir()
    return os.path.join(app_dir, 'medicine_system.db')


def get_backup_dir() -> str:
    app_dir = get_app_data_dir()
    backup_dir = os.path.join(app_dir, 'backups')
    if not os.path.exists(backup_dir):
        os.makedirs(backup_dir)
    return backup_dir


class DatabaseError(Exception):
    pass


class Database:
    _instance = None
    _initialized = False
    _lock = threading.Lock()

    def __new__(cls, db_path: str = None):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super().__new__(cls)
            return cls._instance

    def __init__(self, db_path: str = None):
        with Database._lock:
            if Database._initialized:
                return

            if db_path is None:
                db_path = get_db_path()
            self.db_path = db_path
            self.conn: Optional[sqlite3.Connection] = None
            self.cursor: Optional[sqlite3.Cursor] = None
            self._auto_commit = True
            self._engine: Optional[Any] = None  # 懒加载 SQLAlchemy Engine
            self._connect()
            self._create_tables()
            Database._initialized = True

    @property
    def engine(self):
        """懒加载绑定到 self.db_path 的 SQLAlchemy Engine（单例缓存见 db_session）。"""
        if self._engine is None:
            from core.db_session import get_engine
            self._engine = get_engine(self.db_path)
        return self._engine

    @contextmanager
    def session_scope(self):
        """ORM 会话上下文（独立事务，自动 commit/rollback/close）。

        供 Repository 只读方法使用；写方法在过渡期仍走 sqlite3 路径
        以保持与 Service 层 with self.db.transaction() 的跨 Repository 原子性。
        """
        from core.db_session import session_scope
        with session_scope(self.db_path) as session:
            yield session

    def _connect(self):
        try:
            self.conn = sqlite3.connect(self.db_path, check_same_thread=False)
            self.conn.row_factory = sqlite3.Row
            self.cursor = self.conn.cursor()
            self.cursor.execute('PRAGMA foreign_keys = ON')
        except sqlite3.Error as e:
            raise DatabaseError(f"数据库连接失败: {e}")

    def _create_tables(self):
        """使用 ORM metadata 创建表， supplemented by 手写索引和版本化迁移。

        流程：
        1. Base.metadata.create_all 创建所有表（IF NOT EXISTS 语义）
        2. 创建辅助索引
        3. 执行版本化迁移（_migrate_schema 委托给 core.migrations）
        """
        from core.orm_models import Base
        # 通过 ORM metadata 创建所有表（IF NOT EXISTS 语义）
        Base.metadata.create_all(self.engine)

        # 辅助索引（ORM 未显式定义，需手写）
        indexes = [
            'CREATE INDEX IF NOT EXISTS idx_medicines_name ON medicines (name)',
            'CREATE INDEX IF NOT EXISTS idx_medicines_category ON medicines (category)',
            'CREATE INDEX IF NOT EXISTS idx_inventory_medicine_id ON inventory (medicine_id)',
            'CREATE INDEX IF NOT EXISTS idx_prescriptions_created_at ON prescriptions (created_at)',
            'CREATE INDEX IF NOT EXISTS idx_inventory_history_medicine_id ON inventory_history (medicine_id)',
            # 补充高频查询索引
            'CREATE INDEX IF NOT EXISTS idx_prescription_items_prescription_id ON prescription_items (prescription_id)',
            'CREATE INDEX IF NOT EXISTS idx_prescription_items_medicine_id ON prescription_items (medicine_id)',
            'CREATE INDEX IF NOT EXISTS idx_operation_logs_target_type ON operation_logs (target_type)',
            'CREATE INDEX IF NOT EXISTS idx_inventory_history_created_at ON inventory_history (created_at)',
        ]
        for index_sql in indexes:
            self.cursor.execute(index_sql)

        # 版本化 Schema 迁移：替代手写的全量补列逻辑
        self._migrate_schema()

        self.conn.commit()

    def _migrate_schema(self):
        """版本化迁移入口，委托给 core.migrations.run_pending_migrations。

        迁移操作幂等，已执行的版本通过 schema_migrations 表追踪。
        新增迁移只需在 core.migrations._MIGRATIONS 注册新版本即可。
        """
        from core.migrations import run_pending_migrations
        run_pending_migrations(self.conn)

    def execute(self, query: str, params: tuple = ()) -> sqlite3.Cursor:
        try:
            self.cursor.execute(query, params)
            if self._auto_commit:
                self.conn.commit()
            return self.cursor
        except sqlite3.Error as e:
            if self._auto_commit:
                self.conn.rollback()
            raise DatabaseError(f"执行SQL失败: {e}")

    def fetchall(self, query: str, params: tuple = ()) -> List[Dict]:
        try:
            self.cursor.execute(query, params)
            rows = self.cursor.fetchall()
            return [dict(row) for row in rows]
        except sqlite3.Error as e:
            raise DatabaseError(f"查询失败: {e}")

    def fetchone(self, query: str, params: tuple = ()) -> Optional[Dict]:
        try:
            self.cursor.execute(query, params)
            row = self.cursor.fetchone()
            return dict(row) if row else None
        except sqlite3.Error as e:
            raise DatabaseError(f"查询失败: {e}")

    def begin_transaction(self):
        self._auto_commit = False
        self.cursor.execute('BEGIN TRANSACTION')

    def commit(self):
        self.conn.commit()
        self._auto_commit = True

    def rollback(self):
        self.conn.rollback()
        self._auto_commit = True

    @contextmanager
    def transaction(self):
        self.begin_transaction()
        try:
            yield self
            self.commit()
        except Exception:
            self.rollback()
            raise

    def backup(self) -> str:
        backup_dir = get_backup_dir()
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_path = os.path.join(backup_dir, f'medicine_system_{timestamp}.db')
        shutil.copy2(self.db_path, backup_path)
        return backup_path

    def close(self):
        """关闭连接。

        - 若 self 是当前单例实例：关闭连接并重置单例状态，下次 Database() 会重建。
        - 若 self 是工作线程通过 create_worker_connection() 创建的独立实例：
          仅关闭本连接，不影响单例状态，避免误清主线程的 Database 单例。
        - 幂等：重复调用不会抛异常（便于 fixture teardown 等场景）。
        - 同时释放对应 db_path 的 ORM Engine 缓存。
        """
        try:
            if self.cursor:
                self.cursor.close()
        except sqlite3.ProgrammingError:
            pass
        try:
            if self.conn:
                self.conn.close()
        except sqlite3.ProgrammingError:
            pass
        self.cursor = None
        self.conn = None
        # 释放 ORM Engine 缓存（仅当本实例是单例时，避免 worker 误清主线程 Engine）
        with Database._lock:
            if self is Database._instance:
                self._dispose_engine_safe()
                Database._instance = None
                Database._initialized = False
            else:
                # worker 连接：仅清本实例引用，不动全局 Engine 缓存
                self._engine = None

    def _dispose_engine_safe(self):
        """安全释放 ORM Engine（忽略 db_session 未安装等异常）。"""
        try:
            from core.db_session import dispose_engine
            if self.db_path:
                dispose_engine(self.db_path)
        except Exception:
            pass
        self._engine = None

    def _close_connection(self):
        """仅关闭本连接的 cursor/conn，不触碰单例状态。

        已被 close() 覆盖（close() 现在会自动判断 self 是否为单例），
        保留方法以便已有调用点继续工作，行为等同于 close()。
        """
        if self.cursor:
            self.cursor.close()
        if self.conn:
            self.conn.close()

    @classmethod
    def reset_instance(cls):
        with cls._lock:
            if cls._instance is not None:
                try:
                    cls._instance._close_connection()
                    cls._instance._dispose_engine_safe()
                except Exception:
                    pass
                cls._instance = None
                cls._initialized = False

    @classmethod
    def create_worker_connection(cls, db_path: str = None) -> 'Database':
        """Create a new non-singleton Database connection for use in worker threads."""
        if db_path is None:
            db_path = get_db_path()
        instance = object.__new__(cls)
        instance.db_path = db_path
        instance.conn = None
        instance.cursor = None
        instance._auto_commit = True
        instance._engine = None
        instance._connect()
        return instance
