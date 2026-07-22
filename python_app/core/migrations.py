# -*- coding: utf-8 -*-
"""
版本化 Schema 迁移管理

替代手写的 _migrate_schema 全量补列逻辑，改为按版本号顺序执行增量迁移。
每个迁移版本对应一组幂等的 DDL 操作（ALTER TABLE / CREATE INDEX 等）。

设计原则：
- 每个迁移版本只执行一次（通过 schema_migrations 表追踪）
- 迁移操作必须幂等（可重复执行不报错），用 try/except 包裹 ALTER
- 版本号格式：YYYYMMDD_NNN（日期+序号），单调递增
- 未来可平滑迁移到 Alembic：把 _MIGRATIONS 内容翻译为 alembic revision 即可

现有数据库（旧库）会在首次启动时：
1. 创建 schema_migrations 表
2. 执行 _migrate_schema() 做全量补列（作为 baseline）
3. 标记 20260717_001 baseline 为已执行
4. 后续只执行新增的迁移版本
"""
import sqlite3
from datetime import datetime
from typing import Callable, List, Tuple

# 迁移版本定义：version -> (description, migration_func)
# migration_func 接收 sqlite3.Connection，执行 DDL 操作
_MigrationFunc = Callable[[sqlite3.Connection], None]


def _baseline_migration(conn: sqlite3.Connection) -> None:
    """Baseline 迁移：全量补列旧库缺失的列。

    原 _migrate_schema 的内容，作为版本化迁移的起点。
    对已有列的表执行 ALTER 会失败，用 try/except 忽略。
    """
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

    cursor = conn.cursor()
    for table, columns in migrations.items():
        try:
            cursor.execute(f"PRAGMA table_info({table})")
            existing_cols = {row[1] for row in cursor.fetchall()}
            for col_name, col_def in columns.items():
                if col_name not in existing_cols:
                    try:
                        cursor.execute(
                            f"ALTER TABLE {table} ADD COLUMN {col_name} {col_def}"
                        )
                    except sqlite3.Error:
                        pass
        except sqlite3.Error:
            pass


def _v20260717_002_add_data_version_table(conn: sqlite3.Connection) -> None:
    """迁移 20260717_002：确保 data_version 表存在并初始化默认版本。

    用于追踪数据导入版本（如 300 味药材数据版本），与 schema 迁移分离。
    """
    cursor = conn.cursor()
    try:
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS data_version (
                id INTEGER PRIMARY KEY,
                version TEXT NOT NULL,
                description TEXT,
                applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        # 若表为空则插入初始版本记录
        cursor.execute('SELECT COUNT(*) FROM data_version')
        if cursor.fetchone()[0] == 0:
            cursor.execute(
                "INSERT INTO data_version (version, description) VALUES (?, ?)",
                ('initial', '初始数据版本')
            )
    except sqlite3.Error:
        pass


def _v20260717_003_add_prescription_items_cascade(conn: sqlite3.Connection) -> None:
    """迁移 20260717_003：增强 prescription_items 外键级联删除支持。

    SQLite 不支持 ALTER TABLE 修改外键约束，此迁移仅作为标记。
    实际 CASCADE 行为通过 ORM 的 relationship(cascade='all, delete-orphan') 实现。
    新建库已通过 ORM 定义了正确的 CASCADE，旧库通过应用层保证一致性。
    """
    # SQLite 无法 ALTER 外键约束，此迁移为占位标记，确保 schema_migrations 有完整记录
    pass


def _v20260722_001_create_patients_table(conn: sqlite3.Connection) -> None:
    """迁移 20260722_001：创建患者档案表 patients。

    用于医生管理患者档案，关联历史处方，快速调取患者信息。
    通过 patient.name 与 prescriptions.patient_name 进行业务关联（非外键）。
    """
    cursor = conn.cursor()
    try:
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS patients (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                gender TEXT,
                age INTEGER,
                phone TEXT,
                address TEXT,
                allergy TEXT,
                medical_history TEXT,
                notes TEXT,
                created_at TEXT NOT NULL DEFAULT (datetime('now','localtime')),
                updated_at TEXT NOT NULL DEFAULT (datetime('now','localtime'))
            )
        ''')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_patients_name ON patients(name)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_patients_phone ON patients(phone)')
    except sqlite3.Error:
        pass


def _v20260722_002_alter_patients_add_columns(conn: sqlite3.Connection) -> None:
    """迁移 20260722_002：补全 patients 表缺失列。

    早期版本的 patients 表可能缺少 medical_history 等列（CREATE TABLE IF NOT EXISTS
    不会修改已存在的表）。逐列 ALTER TABLE ADD COLUMN 补全，已存在的列会触发
    sqlite3.Error 并被忽略。
    """
    cursor = conn.cursor()
    columns_to_add = {
        'medical_history': "TEXT",
        'allergy': "TEXT",
        'notes': "TEXT",
        'address': "TEXT",
        'age': "INTEGER",
        'gender': "TEXT",
        'phone': "TEXT",
    }
    for col_name, col_type in columns_to_add.items():
        try:
            cursor.execute(
                f'ALTER TABLE patients ADD COLUMN {col_name} {col_type}'
            )
        except sqlite3.OperationalError:
            pass


# 迁移版本注册表（按版本号升序执行）
_MIGRATIONS: List[Tuple[str, str, _MigrationFunc]] = [
    ('20260717_001', 'Baseline: 全量补列旧库缺失字段', _baseline_migration),
    ('20260717_002', '新增 data_version 表', _v20260717_002_add_data_version_table),
    ('20260717_003', '处方明细级联删除标记', _v20260717_003_add_prescription_items_cascade),
    ('20260722_001', '新增 patients 患者档案表', _v20260722_001_create_patients_table),
    ('20260722_002', '补全 patients 表缺失列（medical_history 等）', _v20260722_002_alter_patients_add_columns),
]


def ensure_schema_migrations_table(conn: sqlite3.Connection) -> None:
    """确保 schema_migrations 表存在"""
    conn.execute('''
        CREATE TABLE IF NOT EXISTS schema_migrations (
            version TEXT PRIMARY KEY,
            description TEXT,
            applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()


def get_applied_versions(conn: sqlite3.Connection) -> set:
    """获取已执行的迁移版本集合"""
    try:
        cursor = conn.execute(
            'SELECT version FROM schema_migrations'
        )
        return {row[0] for row in cursor.fetchall()}
    except sqlite3.Error:
        # schema_migrations 表不存在时返回空集
        return set()


def run_pending_migrations(conn: sqlite3.Connection) -> List[str]:
    """执行所有待执行的迁移版本，返回已执行的版本号列表。

    幂等：已执行的迁移会跳过，未执行的按顺序执行。
    每个迁移在独立事务中执行，失败则回滚该迁移并抛出异常。
    """
    ensure_schema_migrations_table(conn)
    applied = get_applied_versions(conn)
    newly_applied: List[str] = []

    for version, description, migration_func in _MIGRATIONS:
        if version in applied:
            continue
        try:
            # 在事务中执行迁移
            conn.execute('BEGIN')
            migration_func(conn)
            conn.execute(
                'INSERT INTO schema_migrations (version, description, applied_at) VALUES (?, ?, ?)',
                (version, description, datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
            )
            conn.commit()
            newly_applied.append(version)
        except Exception as e:
            conn.rollback()
            raise RuntimeError(f"迁移 {version} 执行失败: {e}") from e

    return newly_applied


def get_pending_versions(conn: sqlite3.Connection) -> List[str]:
    """获取待执行的迁移版本列表（不执行）"""
    ensure_schema_migrations_table(conn)
    applied = get_applied_versions(conn)
    return [v for v, _, _ in _MIGRATIONS if v not in applied]


def get_migration_history() -> List[Tuple[str, str]]:
    """获取所有已注册的迁移版本（用于诊断和文档）"""
    return [(v, d) for v, d, _ in _MIGRATIONS]
