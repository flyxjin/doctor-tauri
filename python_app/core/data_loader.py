# -*- coding: utf-8 -*-
"""
数据加载器 - 内置数据加载和初始化
"""
import time
from typing import Any, Dict, List, Optional, Tuple

from .database import Database
from .logger import get_app_logger, get_data_logger
from .services import DataLoader
from .validators import DataIntegrityValidator


class BuiltinDataLoader:
    BUILTIN_DATA_MODULE = 'medicines_data_300'
    EXPECTED_COUNT = 300

    def __init__(self, db: Database = None):
        self.db = db or Database()
        self.data_loader = DataLoader(self.db)
        self.logger = get_data_logger()
        self.app_logger = get_app_logger()

    def load_builtin_data(self, force: bool = False) -> Tuple[int, int, List[str]]:
        start_time = time.time()

        try:
            builtin_data = self._load_data_from_module()

            if not builtin_data:
                return 0, 0, ["无法加载内置数据"]

            is_valid, errors, warnings = DataIntegrityValidator.validate_medicine_data(builtin_data)

            if warnings:
                for warning in warnings:
                    self.logger.log_data_validation(len(builtin_data), len(builtin_data) - len(warnings), len(warnings))

            added, updated, load_errors = self.data_loader.load_builtin_data(builtin_data, force)

            duration = time.time() - start_time
            self.logger.log_data_load('builtin', added + updated, duration)

            if added > 0 or updated > 0:
                self.app_logger.info(f"内置数据加载完成: 新增 {added}, 更新 {updated}, 耗时 {duration:.2f}秒")

            return added, updated, load_errors

        except Exception as e:
            self.app_logger.error(f"加载内置数据失败: {e}")
            return 0, 0, [str(e)]

    def _load_data_from_module(self) -> Optional[List[Dict]]:
        try:
            # frozen 和非 frozen 都用 import_module（exe 中模块已编译进 PYZ 归档）
            import importlib
            module = importlib.import_module(self.BUILTIN_DATA_MODULE)
            return getattr(module, 'medicines_300', None)
        except ImportError as e:
            self.app_logger.error(f"导入内置数据模块失败: {e}")
        except Exception as e:
            self.app_logger.error(f"加载内置数据时发生错误: {e}")
        return None

    def ensure_data_loaded(self) -> bool:
        count_result = self.db.fetchone('SELECT COUNT(*) as count FROM medicines')
        current_count = count_result['count'] if count_result else 0

        if current_count >= self.EXPECTED_COUNT:
            self.app_logger.info(f"数据库已有 {current_count} 条药材记录，跳过初始化")
            self._repair_missing_inventory()
            return True

        self.app_logger.info(f"数据库当前有 {current_count} 条记录，开始加载内置数据...")

        added, updated, errors = self.load_builtin_data(force=False)

        if errors:
            self.app_logger.warning(f"数据加载过程中出现 {len(errors)} 个错误")
            for error in errors[:5]:
                self.app_logger.warning(f"  - {error}")

        self._repair_missing_inventory()

        count_result = self.db.fetchone('SELECT COUNT(*) as count FROM medicines')
        final_count = count_result['count'] if count_result else 0

        return final_count >= self.EXPECTED_COUNT

    def _repair_missing_inventory(self) -> None:
        """修复 medicines 与 inventory 表数据不一致：为缺失 inventory 记录的药材补建。
        历史数据或批量导入漏建 inventory 会导致库存管理与药材管理种类数不一致。"""
        try:
            missing = self.db.fetchall(
                '''SELECT m.id, m.name FROM medicines m
                   LEFT JOIN inventory i ON m.id = i.medicine_id
                   WHERE i.medicine_id IS NULL'''
            )
            if not missing:
                return
            for row in missing:
                med_id = row['id'] if isinstance(row, dict) else row[0]
                self.db.execute(
                    '''INSERT INTO inventory (medicine_id, quantity, unit, price, min_stock, notes)
                       VALUES (?, 0, 'g', 0, 10, '系统自动补建')''',
                    (med_id,)
                )
            self.app_logger.warning(f"数据修复：为 {len(missing)} 个缺失 inventory 记录的药材自动补建")
        except Exception as e:
            self.app_logger.error(f"修复缺失 inventory 记录失败: {e}")

    def verify_data_integrity(self) -> Tuple[bool, List[str]]:
        return self.data_loader.verify_data_integrity(self.EXPECTED_COUNT)

    def get_data_status(self) -> Dict[str, Any]:
        count_result = self.db.fetchone('SELECT COUNT(*) as count FROM medicines')
        medicine_count = count_result['count'] if count_result else 0

        inv_count = self.db.fetchone('SELECT COUNT(*) as count FROM inventory')
        inventory_count = inv_count['count'] if inv_count else 0

        version_info = self.data_loader.get_data_version()

        is_complete = medicine_count >= self.EXPECTED_COUNT
        is_valid, errors = self.verify_data_integrity()

        return {
            'medicine_count': medicine_count,
            'inventory_count': inventory_count,
            'expected_count': self.EXPECTED_COUNT,
            'is_complete': is_complete,
            'is_valid': is_valid,
            'validation_errors': errors,
            'version': version_info
        }


def initialize_database() -> Database:
    db = Database()

    loader = BuiltinDataLoader(db)
    loader.ensure_data_loaded()

    return db


def get_initialized_db() -> Database:
    return Database()
