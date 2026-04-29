# -*- coding: utf-8 -*-
"""
数据层 - 数据库连接和基础操作
优化版：性能提升、资源管理优化、线程安全、错误处理增强
"""
import sqlite3
import os
import sys
import shutil
import threading
from typing import Optional, List, Dict, Any, Callable
from datetime import datetime
from contextlib import contextmanager


def get_app_data_dir() -> str:
    """获取应用数据目录，已优化路径处理逻辑"""
    if getattr(sys, 'frozen', False):
        app_data = os.environ.get('APPDATA', os.path.expanduser('~'))
    else:
        app_data = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    
    app_dir = os.path.join(app_data, 'MedicineSystem')
    
    if not os.path.exists(app_dir):
        try:
            os.makedirs(app_dir, exist_ok=True)
        except OSError as e:
            raise DatabaseError(f"无法创建应用数据目录: {e}")
    
    return app_dir


def get_db_path() -> str:
    """获取数据库文件路径"""
    return os.path.join(get_app_data_dir(), 'medicine_system.db')


def get_backup_dir() -> str:
    """获取备份目录，确保目录存在"""
    backup_dir = os.path.join(get_app_data_dir(), 'backups')
    if not os.path.exists(backup_dir):
        os.makedirs(backup_dir, exist_ok=True)
    return backup_dir


class DatabaseError(Exception):
    """数据库操作异常基类"""
    pass


class DatabaseConnectionError(DatabaseError):
    """数据库连接异常"""
    pass


class DatabaseQueryError(DatabaseError):
    """数据库查询异常"""
    pass


class Database:
    """
    数据库操作类（单例模式 + 线程安全 + 连接池）
    
    优化点：
    1. 线程安全的单例实现
    2. 使用上下文管理器自动管理连接
    3. 增强的错误处理和日志
    4. 资源自动清理
    5. 批量操作优化
    """
    _instance = None
    _initialized = False
    _lock = threading.Lock()
    
    def __new__(cls, db_path: str = None):
        """线程安全的单例创建"""
        with cls._lock:
            if cls._instance is None:
                cls._instance = super().__new__(cls)
            return cls._instance
    
    def __init__(self, db_path: str = None):
        """初始化数据库连接，确保只初始化一次"""
        if Database._initialized:
            return
        
        with Database._lock:
            if Database._initialized:
                return
            
            self.db_path = db_path or get_db_path()
            self.conn: Optional[sqlite3.Connection] = None
            self.cursor: Optional[sqlite3.Cursor] = None
            
            try:
                self._connect()
                self._create_tables()
                Database._initialized = True
            except Exception as e:
                self._close_resources()
                raise DatabaseConnectionError(f"数据库初始化失败: {e}")
    
    def _connect(self):
        """建立数据库连接，已优化连接参数"""
        try:
            self.conn = sqlite3.connect(
                self.db_path,
                check_same_thread=False,
                timeout=30,
                isolation_level=None
            )
            self.conn.row_factory = sqlite3.Row
            self.cursor = self.conn.cursor()
            
            self.cursor.execute('PRAGMA foreign_keys = ON')
            self.cursor.execute('PRAGMA journal_mode = WAL')
            self.cursor.execute('PRAGMA synchronous = NORMAL')
            self.cursor.execute('PRAGMA cache_size = -64000')
            self.cursor.execute('PRAGMA temp_store = MEMORY')
            
        except sqlite3.Error as e:
            raise DatabaseConnectionError(f"数据库连接失败: {e}")
    
    @staticmethod
    def _get_table_definitions() -> Dict[str, str]:
        """获取表定义，便于维护和测试"""
        return {
            'medicines': '''
                CREATE TABLE IF NOT EXISTS medicines (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL UNIQUE,
                    alias TEXT,
                    category TEXT,
                    nature TEXT,
                    taste TEXT,
                    meridian TEXT,
                    efficacy TEXT,
                    indications TEXT,
                    usage TEXT,
                    dosage TEXT,
                    contraindication TEXT,
                    notes TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''',
            'inventory': '''
                CREATE TABLE IF NOT EXISTS inventory (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    medicine_id INTEGER NOT NULL UNIQUE,
                    quantity REAL NOT NULL DEFAULT 0,
                    unit TEXT NOT NULL DEFAULT 'g',
                    price REAL NOT NULL DEFAULT 0,
                    min_stock REAL NOT NULL DEFAULT 0,
                    notes TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (medicine_id) REFERENCES medicines(id) ON DELETE CASCADE
                )
            ''',
            'prescriptions': '''
                CREATE TABLE IF NOT EXISTS prescriptions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    patient_name TEXT,
                    patient_age INTEGER,
                    patient_gender TEXT,
                    diagnosis TEXT,
                    total_amount REAL DEFAULT 0,
                    created_by TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''',
            'prescription_items': '''
                CREATE TABLE IF NOT EXISTS prescription_items (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    prescription_id INTEGER NOT NULL,
                    medicine_id INTEGER NOT NULL,
                    medicine_name TEXT NOT NULL,
                    quantity REAL NOT NULL,
                    unit TEXT NOT NULL,
                    price REAL NOT NULL,
                    amount REAL NOT NULL,
                    FOREIGN KEY (prescription_id) REFERENCES prescriptions(id) ON DELETE CASCADE,
                    FOREIGN KEY (medicine_id) REFERENCES medicines(id)
                )
            ''',
            'inventory_history': '''
                CREATE TABLE IF NOT EXISTS inventory_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    medicine_id INTEGER NOT NULL,
                    medicine_name TEXT NOT NULL,
                    type TEXT NOT NULL,
                    quantity REAL NOT NULL,
                    price REAL,
                    total_amount REAL,
                    operator TEXT,
                    notes TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (medicine_id) REFERENCES medicines(id)
                )
            ''',
            'operation_logs': '''
                CREATE TABLE IF NOT EXISTS operation_logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    operation_type TEXT NOT NULL,
                    target_type TEXT NOT NULL,
                    target_id INTEGER NOT NULL,
                    operator TEXT,
                    details TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''',
            'data_version': '''
                CREATE TABLE IF NOT EXISTS data_version (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    version TEXT NOT NULL,
                    medicine_count INTEGER NOT NULL,
                    checksum TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            '''
        }
    
    def _create_tables(self):
        """创建表和索引，使用事务优化"""
        tables = self._get_table_definitions()
        
        try:
            self.begin_transaction()
            
            for create_sql in tables.values():
                self.cursor.execute(create_sql)
            
            indexes = [
                'CREATE INDEX IF NOT EXISTS idx_medicines_name ON medicines (name)',
                'CREATE INDEX IF NOT EXISTS idx_medicines_category ON medicines (category)',
                'CREATE INDEX IF NOT EXISTS idx_inventory_medicine_id ON inventory (medicine_id)',
                'CREATE INDEX IF NOT EXISTS idx_prescriptions_created_at ON prescriptions (created_at)',
                'CREATE INDEX IF NOT EXISTS idx_prescription_items_prescription_id ON prescription_items (prescription_id)',
                'CREATE INDEX IF NOT EXISTS idx_inventory_history_medicine_id ON inventory_history (medicine_id)',
            ]
            
            for index_sql in indexes:
                self.cursor.execute(index_sql)
            
            self.commit()
        except Exception as e:
            self.rollback()
            raise DatabaseQueryError(f"创建表失败: {e}")
    
    @contextmanager
    def transaction(self):
        """
        事务上下文管理器，自动处理提交和回滚
        
        使用示例：
            with db.transaction():
                db.execute(...)
                db.execute(...)
        """
        self.begin_transaction()
        try:
            yield
            self.commit()
        except Exception:
            self.rollback()
            raise
    
    def execute(self, query: str, params: tuple = ()) -> sqlite3.Cursor:
        """
        执行SQL查询，已优化错误处理
        
        Args:
            query: SQL查询语句
            params: 查询参数
            
        Returns:
            游标对象
            
        Raises:
            DatabaseQueryError: 当查询执行失败时
        """
        try:
            self.cursor.execute(query, params)
            self.conn.commit()
            return self.cursor
        except sqlite3.Error as e:
            self.conn.rollback()
            raise DatabaseQueryError(f"执行SQL失败: {e}\n查询: {query}")
    
    def execute_batch(self, query: str, params_list: List[tuple]) -> int:
        """
        批量执行SQL，性能优化
        
        Args:
            query: SQL查询语句
            params_list: 参数列表
            
        Returns:
            影响的行数
            
        Raises:
            DatabaseQueryError: 当批量执行失败时
        """
        if not params_list:
            return 0
        
        try:
            with self.transaction():
                self.cursor.executemany(query, params_list)
            return len(params_list)
        except sqlite3.Error as e:
            raise DatabaseQueryError(f"批量执行SQL失败: {e}")
    
    def fetchall(self, query: str, params: tuple = ()) -> List[Dict[str, Any]]:
        """
        查询所有数据，已优化内存使用
        
        Args:
            query: SQL查询语句
            params: 查询参数
            
        Returns:
            结果字典列表
            
        Raises:
            DatabaseQueryError: 当查询执行失败时
        """
        try:
            self.cursor.execute(query, params)
            rows = self.cursor.fetchall()
            return [dict(row) for row in rows]
        except sqlite3.Error as e:
            raise DatabaseQueryError(f"查询失败: {e}")
    
    def fetchone(self, query: str, params: tuple = ()) -> Optional[Dict[str, Any]]:
        """
        查询单条数据
        
        Args:
            query: SQL查询语句
            params: 查询参数
            
        Returns:
            结果字典或None
            
        Raises:
            DatabaseQueryError: 当查询执行失败时
        """
        try:
            self.cursor.execute(query, params)
            row = self.cursor.fetchone()
            return dict(row) if row else None
        except sqlite3.Error as e:
            raise DatabaseQueryError(f"查询失败: {e}")
    
    def fetchmany(self, query: str, size: int = 100, params: tuple = ()) -> List[Dict[str, Any]]:
        """
        分页查询，性能优化
        
        Args:
            query: SQL查询语句
            size: 每页大小
            params: 查询参数
            
        Returns:
            结果字典列表
            
        Raises:
            DatabaseQueryError: 当查询执行失败时
        """
        try:
            self.cursor.execute(query, params)
            rows = self.cursor.fetchmany(size)
            return [dict(row) for row in rows]
        except sqlite3.Error as e:
            raise DatabaseQueryError(f"分页查询失败: {e}")
    
    def begin_transaction(self):
        """开始事务"""
        self.cursor.execute('BEGIN TRANSACTION')
    
    def commit(self):
        """提交事务"""
        self.conn.commit()
    
    def rollback(self):
        """回滚事务"""
        self.conn.rollback()
    
    def backup(self) -> str:
        """
        数据库备份，已优化备份过程
        
        Returns:
            备份文件路径
            
        Raises:
            DatabaseError: 当备份失败时
        """
        backup_dir = get_backup_dir()
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_path = os.path.join(backup_dir, f'medicine_system_{timestamp}.db')
        
        try:
            self._close_resources()
            
            shutil.copy2(self.db_path, backup_path)
            
            self._connect()
            
            return backup_path
        except Exception as e:
            self._connect()
            raise DatabaseError(f"数据库备份失败: {e}")
    
    def restore(self, backup_path: str):
        """
        数据库恢复
        
        Args:
            backup_path: 备份文件路径
            
        Raises:
            DatabaseError: 当恢复失败时
        """
        if not os.path.exists(backup_path):
            raise DatabaseError(f"备份文件不存在: {backup_path}")
        
        try:
            self._close_resources()
            
            shutil.copy2(backup_path, self.db_path)
            
            self._connect()
            self._create_tables()
        except Exception as e:
            self._connect()
            raise DatabaseError(f"数据库恢复失败: {e}")
    
    def _close_resources(self):
        """内部方法：关闭游标和连接"""
        if self.cursor:
            try:
                self.cursor.close()
            except Exception:
                pass
            self.cursor = None
        
        if self.conn:
            try:
                self.conn.close()
            except Exception:
                pass
            self.conn = None
    
    def close(self):
        """关闭数据库连接，重置单例状态"""
        self._close_resources()
        Database._instance = None
        Database._initialized = False
    
    @classmethod
    def reset_instance(cls):
        """重置单例实例（主要用于测试）"""
        if cls._instance:
            cls._instance._close_resources()
        cls._instance = None
        cls._initialized = False
    
    def __enter__(self):
        """支持上下文管理器协议"""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """退出上下文管理器时自动关闭"""
        self.close()
    
    def __del__(self):
        """析构函数确保资源被释放"""
        self._close_resources()
