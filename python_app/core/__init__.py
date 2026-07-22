# -*- coding: utf-8 -*-
"""
核心模块包
包含数据层、服务层、模型层和工具层
"""

from .cache import LRUCache, MedicineCache, get_medicine_cache, invalidate_medicine_cache
from .compatibility import (
    INCOMPATIBLE_PAIRS,
    check_against_existing,
    check_compatibility,
    check_pair,
)
from .compatibility import (
    reload_rules as reload_compatibility_rules,
)
from .data_loader import BuiltinDataLoader, get_initialized_db, initialize_database
from .database import Database, DatabaseError, get_app_data_dir, get_backup_dir, get_db_path
from .exceptions import (
    AppException,
    CacheException,
    DatabaseException,
    ErrorCode,
    InventoryException,
    Result,
    ServiceException,
    ValidationException,
    handle_exception,
    safe_execute,
)
from .logger import DataLogger, OperationLogger, get_app_logger, get_data_logger, get_logger, get_operation_logger
from .models import Inventory, InventoryHistory, Medicine, OperationLog, Patient, Prescription, PrescriptionItem
from .performance import (
    PerformanceMonitor,
    Timer,
    get_performance_monitor,
    measure,
    performance_report,
    print_performance_report,
)
from .services import (
    DashboardService,
    DataLoader,
    InventoryService,
    MedicineService,
    PatientService,
    PrescriptionService,
    ServiceError,
    StatisticsService,
)
from .validators import DataIntegrityValidator, MedicineValidator, PrescriptionValidator, ValidationError

__all__ = [
    'Database', 'get_db_path', 'get_app_data_dir', 'get_backup_dir', 'DatabaseError',
    'Medicine', 'Prescription', 'PrescriptionItem', 'Inventory', 'InventoryHistory', 'OperationLog', 'Patient',
    'MedicineService', 'PrescriptionService', 'InventoryService', 'DataLoader',
    'DashboardService', 'StatisticsService', 'PatientService', 'ServiceError',
    'MedicineValidator', 'PrescriptionValidator', 'DataIntegrityValidator', 'ValidationError',
    'get_logger', 'get_app_logger', 'get_operation_logger', 'get_data_logger', 'OperationLogger', 'DataLogger',
    'BuiltinDataLoader', 'initialize_database', 'get_initialized_db',
    'MedicineCache', 'get_medicine_cache', 'invalidate_medicine_cache', 'LRUCache',
    'PerformanceMonitor', 'get_performance_monitor', 'measure', 'Timer', 'performance_report', 'print_performance_report',
    'AppException', 'DatabaseException', 'ValidationException', 'ServiceException',
    'InventoryException', 'CacheException', 'Result', 'ErrorCode', 'handle_exception', 'safe_execute',
    'INCOMPATIBLE_PAIRS', 'check_pair', 'check_compatibility', 'check_against_existing',
    'reload_compatibility_rules',
]
