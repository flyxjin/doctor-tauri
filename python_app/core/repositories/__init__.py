# -*- coding: utf-8 -*-
"""
Repository 层 - 数据访问

职责：仅负责 SQL/ORM 操作，不包含业务逻辑、验证、缓存。
Service 层通过 Repository 访问数据，保持职责分离。

阶段 1（当前）：Repository 内部仍使用原生 SQL（包装 Database.execute/fetchall/fetchone）。
阶段 2：Repository 内部切换到 SQLAlchemy ORM，对外接口不变。
"""
from .base import BaseRepository
from .inventory_repo import InventoryRepository
from .medicine_repo import MedicineRepository
from .operation_log_repo import OperationLogRepository
from .patient_repo import PatientRepository
from .prescription_repo import PrescriptionRepository
from .statistics_repo import StatisticsRepository

__all__ = [
    'BaseRepository',
    'MedicineRepository',
    'InventoryRepository',
    'PrescriptionRepository',
    'OperationLogRepository',
    'StatisticsRepository',
    'PatientRepository',
]
