# -*- coding: utf-8 -*-
"""
操作日志数据访问 Repository

收纳原 services._log_operation 的数据访问；保留模块级兼容函数 _log_operation。

阶段 2.3：只读方法切换到 SQLAlchemy ORM；写方法保留 SQL（等阶段 2.4 统一切换）。
"""
from typing import Any, Dict, List

from sqlalchemy import select

from ..orm_models import OperationLogORM
from .base import BaseRepository


class OperationLogRepository(BaseRepository):
    """operation_logs 表的数据访问。"""

    # ---- 只读（已切换 ORM） ----
    def find_all(self, limit: int = 100) -> List[Dict[str, Any]]:
        with self._session_scope() as session:
            stmt = (
                select(OperationLogORM)
                .order_by(OperationLogORM.created_at.desc())
                .limit(limit)
            )
            rows = session.execute(stmt).scalars().all()
            return [self._orm_to_dict(log) for log in rows]

    def find_by_target_type(self, target_type: str, limit: int = 100) -> List[Dict[str, Any]]:
        """按目标类型查询操作日志（替代 history_view 直接查 operation_logs 表）"""
        with self._session_scope() as session:
            stmt = (
                select(
                    OperationLogORM.operation_type.label('operation_type'),
                    OperationLogORM.target_type.label('target_type'),
                    OperationLogORM.target_id.label('target_id'),
                    OperationLogORM.operator.label('operator'),
                    OperationLogORM.created_at.label('created_at'),
                )
                .where(OperationLogORM.target_type == target_type)
                .order_by(OperationLogORM.created_at.desc())
                .limit(limit)
            )
            return [dict(row._mapping) for row in session.execute(stmt).all()]

    # ---- 写（保留 SQL，等阶段 2.4 统一切换） ----
    def insert(self, operation_type: str, target_type: str,
               target_id: int, details: str = '') -> None:
        self.execute(
            '''INSERT INTO operation_logs (operation_type, target_type, target_id, details)
               VALUES (?, ?, ?, ?)''',
            (operation_type, target_type, target_id, details)
        )
