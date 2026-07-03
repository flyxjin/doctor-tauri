# -*- coding: utf-8 -*-
"""
数据层 - 数据库连接和基础操作
"""
import sqlite3
import os
import sys
import shutil
import threading
from typing import Optional, List, Dict, Any
from contextlib import contextmanager
from datetime import datetime


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
            self._connect()
            self._create_tables()
            Database._initialized = True
    
    def _connect(self):
        try:
            self.conn = sqlite3.connect(self.db_path, check_same_thread=False)
            self.conn.row_factory = sqlite3.Row
            self.cursor = self.conn.cursor()
            self.cursor.execute('PRAGMA foreign_keys = ON')
        except sqlite3.Error as e:
            raise DatabaseError(f"数据库连接失败: {e}")
    
    def _create_tables(self):
        tables = {
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
        
        for table_name, create_sql in tables.items():
            self.cursor.execute(create_sql)
        
        indexes = [
            'CREATE INDEX IF NOT EXISTS idx_medicines_name ON medicines (name)',
            'CREATE INDEX IF NOT EXISTS idx_medicines_category ON medicines (category)',
            'CREATE INDEX IF NOT EXISTS idx_inventory_medicine_id ON inventory (medicine_id)',
            'CREATE INDEX IF NOT EXISTS idx_prescriptions_created_at ON prescriptions (created_at)',
            'CREATE INDEX IF NOT EXISTS idx_inventory_history_medicine_id ON inventory_history (medicine_id)',
        ]
        
        for index_sql in indexes:
            self.cursor.execute(index_sql)

        # Schema 迁移：检测并补全旧数据库缺失的列
        self._migrate_schema()

        self.conn.commit()

    def _migrate_schema(self):
        """检测并添加旧数据库中缺失的列，保证 schema 与当前代码一致"""
        # 注意：SQLite ALTER TABLE ADD COLUMN 不支持非常量默认值（如 CURRENT_TIMESTAMP）
        # 时间戳列迁移时不带 DEFAULT，由代码在 INSERT/UPDATE 时设置
        migrations = {
            'medicines': {
                'alias': "TEXT",
                'category': "TEXT",
                'nature': "TEXT",
                'taste': "TEXT",
                'meridian': "TEXT",
                'efficacy': "TEXT",
                'indications': "TEXT",
                'usage': "TEXT",
                'dosage': "TEXT",
                'contraindication': "TEXT",
                'notes': "TEXT",
                'created_at': "TIMESTAMP",
                'updated_at': "TIMESTAMP",
            },
            'inventory': {
                'quantity': "REAL DEFAULT 0",
                'unit': "TEXT DEFAULT 'g'",
                'price': "REAL DEFAULT 0",
                'min_stock': "REAL DEFAULT 0",
                'notes': "TEXT",
                'created_at': "TIMESTAMP",
                'updated_at': "TIMESTAMP",
            },
            'prescriptions': {
                'patient_name': "TEXT",
                'patient_age': "INTEGER",
                'patient_gender': "TEXT",
                'diagnosis': "TEXT",
                'total_amount': "REAL DEFAULT 0",
                'created_by': "TEXT",
                'created_at': "TIMESTAMP",
            },
            'prescription_items': {
                'prescription_id': "INTEGER",
                'medicine_id': "INTEGER",
                'medicine_name': "TEXT",
                'quantity': "REAL DEFAULT 0",
                'unit': "TEXT DEFAULT 'g'",
                'price': "REAL DEFAULT 0",
                'amount': "REAL DEFAULT 0",
            },
            'inventory_history': {
                'medicine_id': "INTEGER",
                'medicine_name': "TEXT",
                'type': "TEXT",
                'quantity': "REAL DEFAULT 0",
                'price': "REAL",
                'total_amount': "REAL",
                'operator': "TEXT",
                'notes': "TEXT",
                'created_at': "TIMESTAMP",
            },
            'operation_logs': {
                'operation_type': "TEXT",
                'target_type': "TEXT",
                'target_id': "INTEGER",
                'operator': "TEXT",
                'details': "TEXT",
                'created_at': "TIMESTAMP",
            },
        }

        for table, columns in migrations.items():
            try:
                self.cursor.execute(f"PRAGMA table_info({table})")
                existing_cols = {row[1] for row in self.cursor.fetchall()}
                for col_name, col_def in columns.items():
                    if col_name not in existing_cols:
                        try:
                            self.cursor.execute(
                                f"ALTER TABLE {table} ADD COLUMN {col_name} {col_def}"
                            )
                        except sqlite3.Error:
                            pass
            except sqlite3.Error:
                pass
    
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
        if self.cursor:
            self.cursor.close()
        if self.conn:
            self.conn.close()
        with Database._lock:
            Database._instance = None
            Database._initialized = False

    def _close_connection(self):
        """Close DB connection without touching singleton state (used by reset_instance)."""
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
        instance._connect()
        return instance
