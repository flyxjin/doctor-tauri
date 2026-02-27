# -*- coding: utf-8 -*-
"""
核心模块包 - Windows 7 兼容版本
包含数据层、服务层、模型层和工具层
新增Windows 7兼容性适配模块
"""

from .database import Database, get_db_path, get_app_data_dir, get_backup_dir, DatabaseError
from .models import Medicine, Prescription, PrescriptionItem, Inventory, InventoryHistory, OperationLog
from .services import MedicineService, PrescriptionService, InventoryService, DataLoader, ServiceError
from .validators import MedicineValidator, PrescriptionValidator, InventoryValidator, DataIntegrityValidator, ValidationError
from .logger import get_logger, get_app_logger, get_operation_logger, get_data_logger, OperationLogger, DataLogger
from .data_loader import BuiltinDataLoader, initialize_database, get_initialized_db
from .cache import MedicineCache, get_medicine_cache, invalidate_medicine_cache, LRUCache
from .performance import PerformanceMonitor, get_performance_monitor, measure, Timer, performance_report, print_performance_report
from .exceptions import (
    AppException, DatabaseException, ValidationException, ServiceException,
    InventoryException, CacheException, Result, ErrorCode, handle_exception, safe_execute
)
from .config import ConfigManager, get_config, AppConfig, DatabaseConfig, CacheConfig, PerformanceConfig, UIConfig
from .win7_compat import Windows7Compat, initialize_win7_compat, get_win7_compat

__all__ = [
    'Database', 'get_db_path', 'get_app_data_dir', 'get_backup_dir', 'DatabaseError',
    'Medicine', 'Prescription', 'PrescriptionItem', 'Inventory', 'InventoryHistory', 'OperationLog',
    'MedicineService', 'PrescriptionService', 'InventoryService', 'DataLoader', 'ServiceError',
    'MedicineValidator', 'PrescriptionValidator', 'InventoryValidator', 'DataIntegrityValidator', 'ValidationError',
    'get_logger', 'get_app_logger', 'get_operation_logger', 'get_data_logger', 'OperationLogger', 'DataLogger',
    'BuiltinDataLoader', 'initialize_database', 'get_initialized_db',
    'MedicineCache', 'get_medicine_cache', 'invalidate_medicine_cache', 'LRUCache',
    'PerformanceMonitor', 'get_performance_monitor', 'measure', 'Timer', 'performance_report', 'print_performance_report',
    'AppException', 'DatabaseException', 'ValidationException', 'ServiceException',
    'InventoryException', 'CacheException', 'Result', 'ErrorCode', 'handle_exception', 'safe_execute',
    'ConfigManager', 'get_config', 'AppConfig', 'DatabaseConfig', 'CacheConfig', 'PerformanceConfig', 'UIConfig',
    'Windows7Compat', 'initialize_win7_compat', 'get_win7_compat'
]
