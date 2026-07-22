# -*- coding: utf-8 -*-
"""
版本化 Schema 迁移系统单元测试

验证迁移幂等性、版本追踪、baseline 补列等行为。
"""
import os
import sqlite3
import tempfile

import pytest

from core.migrations import (
    ensure_schema_migrations_table,
    get_applied_versions,
    get_migration_history,
    get_pending_versions,
    run_pending_migrations,
)


@pytest.fixture
def empty_db():
    """创建一个空数据库（无任何业务表）"""
    fd, path = tempfile.mkstemp(suffix='.db')
    os.close(fd)
    conn = sqlite3.connect(path)
    yield conn
    conn.close()
    if os.path.exists(path):
        os.unlink(path)


@pytest.fixture
def fresh_db(empty_db):
    """创建带 schema_migrations 表但无任何迁移执行的数据库"""
    ensure_schema_migrations_table(empty_db)
    return empty_db


class TestSchemaMigrationsTable:
    """schema_migrations 表管理测试"""

    def test_ensure_table_creates_if_not_exists(self, empty_db):
        """ensure_schema_migrations_table 应创建表"""
        # 先验证表不存在
        cursor = empty_db.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='schema_migrations'"
        )
        assert cursor.fetchone() is None

        ensure_schema_migrations_table(empty_db)

        cursor = empty_db.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='schema_migrations'"
        )
        assert cursor.fetchone() is not None

    def test_ensure_table_is_idempotent(self, fresh_db):
        """重复调用 ensure_schema_migrations_table 不报错"""
        ensure_schema_migrations_table(fresh_db)
        ensure_schema_migrations_table(fresh_db)


class TestAppliedVersions:
    """已执行版本查询测试"""

    def test_empty_db_returns_empty_set(self, fresh_db):
        """空库的已执行版本集合应为空"""
        assert get_applied_versions(fresh_db) == set()

    def test_returns_applied_versions(self, fresh_db):
        """应返回已记录的版本"""
        fresh_db.execute(
            "INSERT INTO schema_migrations (version, description) VALUES (?, ?)",
            ('20260717_001', 'Baseline')
        )
        fresh_db.commit()
        assert get_applied_versions(fresh_db) == {'20260717_001'}

    def test_handles_missing_table(self, empty_db):
        """schema_migrations 表不存在时应返回空集（不抛异常）"""
        assert get_applied_versions(empty_db) == set()


class TestRunPendingMigrations:
    """迁移执行测试"""

    def test_fresh_db_executes_all_migrations(self, empty_db):
        """空库应执行所有已注册的迁移版本"""
        newly = run_pending_migrations(empty_db)
        history = get_migration_history()
        # 应执行所有迁移
        assert len(newly) == len(history)
        # 所有版本都应记录在 schema_migrations
        applied = get_applied_versions(empty_db)
        for version, _ in history:
            assert version in applied

    def test_migrations_are_idempotent(self, empty_db):
        """重复执行迁移不应重复执行已应用的版本"""
        run_pending_migrations(empty_db)
        newly_second = run_pending_migrations(empty_db)
        assert newly_second == []

    def test_baseline_creates_missing_columns(self, empty_db):
        """baseline 迁移应给已有表补列"""
        # 模拟旧库：创建一个缺列的 medicines 表
        empty_db.execute('''
            CREATE TABLE medicines (
                id INTEGER PRIMARY KEY,
                name TEXT
            )
        ''')
        empty_db.commit()

        run_pending_migrations(empty_db)

        # 验证补列成功
        cursor = empty_db.execute('PRAGMA table_info(medicines)')
        cols = {row[1] for row in cursor.fetchall()}
        assert 'alias' in cols
        assert 'category' in cols
        assert 'efficacy' in cols
        assert 'created_at' in cols

    def test_data_version_table_created(self, empty_db):
        """迁移 20260717_002 应创建 data_version 表并初始化默认版本"""
        run_pending_migrations(empty_db)
        cursor = empty_db.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='data_version'"
        )
        assert cursor.fetchone() is not None

        cursor = empty_db.execute('SELECT COUNT(*) FROM data_version')
        assert cursor.fetchone()[0] >= 1

    def test_migration_failure_rolls_back(self, fresh_db):
        """迁移失败时应回滚事务，版本不记录"""
        # 手动注入一个会失败的迁移到 _MIGRATIONS（通过 monkeypatch）
        from core import migrations as mig_module

        def _failing_migration(conn):
            raise ValueError("故意失败")

        original = mig_module._MIGRATIONS[:]
        try:
            mig_module._MIGRATIONS.append(
                ('999999_999', 'Failing migration', _failing_migration)
            )
            with pytest.raises(RuntimeError, match='999999_999'):
                run_pending_migrations(fresh_db)
            # 失败版本不应记录
            applied = get_applied_versions(fresh_db)
            assert '999999_999' not in applied
        finally:
            mig_module._MIGRATIONS = original


class TestPendingVersions:
    """待执行版本查询测试"""

    def test_empty_db_all_pending(self, empty_db):
        """空库所有迁移都是待执行状态"""
        pending = get_pending_versions(empty_db)
        history = get_migration_history()
        assert len(pending) == len(history)

    def test_no_pending_after_run(self, empty_db):
        """执行后应无待执行版本"""
        run_pending_migrations(empty_db)
        assert get_pending_versions(empty_db) == []


class TestMigrationHistory:
    """迁移历史查询测试"""

    def test_returns_all_registered_versions(self):
        """get_migration_history 返回所有已注册的迁移版本"""
        history = get_migration_history()
        assert len(history) >= 3
        # 验证格式 (version, description)
        for item in history:
            assert len(item) == 2
            assert isinstance(item[0], str)

    def test_baseline_version_exists(self):
        """baseline 版本应在历史中"""
        history = get_migration_history()
        versions = [v for v, _ in history]
        assert '20260717_001' in versions
