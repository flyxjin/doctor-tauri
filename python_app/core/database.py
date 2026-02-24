# -*- coding: utf-8 -*-
"""
数据层 - 数据库连接和基础操作
"""
import sqlite3
import os
import sys
import shutil
from typing import Optional, List, Dict, Any
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
    
    def __new__(cls, db_path: str = None):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self, db_path: str = None):
        if Database._initialized:
            return
        
        if db_path is None:
            db_path = get_db_path()
        self.db_path = db_path
        self.conn: Optional[sqlite3.Connection] = None
        self.cursor: Optional[sqlite3.Cursor] = None
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
        
        self.conn.commit()
    
    def execute(self, query: str, params: tuple = ()) -> sqlite3.Cursor:
        try:
            self.cursor.execute(query, params)
            self.conn.commit()
            return self.cursor
        except sqlite3.Error as e:
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
        self.cursor.execute('BEGIN TRANSACTION')
    
    def commit(self):
        self.conn.commit()
    
    def rollback(self):
        self.conn.rollback()
    
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
        Database._instance = None
        Database._initialized = False
    
    @classmethod
    def reset_instance(cls):
        cls._instance = None
        cls._initialized = False
