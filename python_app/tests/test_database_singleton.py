# -*- coding: utf-8 -*-
"""
Database 单例与工作线程连接回归测试

回归场景：批量导入完成后，worker 线程调用 db.close() 误清主线程单例状态，
导致后续 Database() 创建第二条连接，引发 "database is locked" 或缓存不一致。
"""
import threading

from core.database import Database


class TestDatabaseSingleton:
    def test_worker_close_does_not_reset_singleton(self, temp_db):
        """worker 线程通过 create_worker_connection() 创建的连接 close() 后，
        不应重置主线程的单例状态。"""
        # 主线程单例
        main_db = Database()
        assert main_db is temp_db
        assert Database._initialized is True
        assert Database._instance is main_db

        # 模拟 worker 线程创建独立连接
        worker_db = Database.create_worker_connection(temp_db.db_path)
        assert worker_db is not main_db
        # worker 连接可用
        row = worker_db.fetchone("SELECT 1 AS v")
        assert row['v'] == 1

        # worker 关闭连接（这是 batch_import_view 的 finally 行为）
        worker_db.close()

        # 关键回归点：主线程单例状态应保持不变
        assert Database._instance is main_db, "worker close() 误清了主线程单例"
        assert Database._initialized is True, "worker close() 误清了单例初始化标志"

        # 主线程连接仍可用
        row = main_db.fetchone("SELECT 1 AS v")
        assert row['v'] == 1

        # Database() 仍返回同一个单例（不会重建）
        assert Database() is main_db

    def test_main_close_resets_singleton(self, temp_db):
        """主线程单例调用 close() 应重置单例状态，允许下次重建。"""
        main_db = Database()
        assert Database._instance is main_db

        main_db.close()

        assert Database._instance is None
        assert Database._initialized is False

        # 重新创建应得到新实例
        new_db = Database(temp_db.db_path)
        assert new_db is not main_db
        assert Database._instance is new_db
        new_db.close()

    def test_worker_close_in_thread_does_not_reset_singleton(self, temp_db):
        """在真实子线程中关闭 worker 连接，主线程单例应保持不变。"""
        main_db = Database()
        assert Database._instance is main_db

        worker_db = Database.create_worker_connection(temp_db.db_path)
        error_box = []

        def worker():
            try:
                # 模拟 ImportWorker.run 的 finally
                worker_db._close_connection()
            except Exception as e:
                error_box.append(e)

        t = threading.Thread(target=worker)
        t.start()
        t.join()

        assert not error_box, f"worker 线程关闭异常: {error_box}"
        # 主线程单例仍存活
        assert Database._instance is main_db, "子线程 close() 误清主线程单例"
        row = main_db.fetchone("SELECT 1 AS v")
        assert row['v'] == 1
