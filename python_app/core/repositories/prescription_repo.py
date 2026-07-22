# -*- coding: utf-8 -*-
"""
处方数据访问 Repository

从 PrescriptionService 抽取的全部数据访问操作。

阶段 2.3：只读方法切换到 SQLAlchemy ORM；写方法保留 SQL（等阶段 2.4 统一切换）。
"""
from typing import Any, Dict, List, Optional

from sqlalchemy import and_, func, select

from ..orm_models import PrescriptionItemORM, PrescriptionORM
from .base import BaseRepository


class PrescriptionRepository(BaseRepository):
    """prescriptions 与 prescription_items 表的数据访问。"""

    # ====================================================================
    # 只读方法（已切换 ORM）
    # ====================================================================
    def find_by_id(self, prescription_id: int) -> Optional[Dict[str, Any]]:
        with self._session_scope() as session:
            stmt = select(PrescriptionORM).where(PrescriptionORM.id == prescription_id)
            p = session.execute(stmt).scalars().first()
            return self._orm_to_dict(p) if p else None

    def find_items(self, prescription_id: int) -> List[Dict[str, Any]]:
        with self._session_scope() as session:
            stmt = (
                select(PrescriptionItemORM)
                .where(PrescriptionItemORM.prescription_id == prescription_id)
            )
            rows = session.execute(stmt).scalars().all()
            return [self._orm_to_dict(item) for item in rows]

    def find_all(self, start_date: str = None, end_date: str = None,
                 patient_name: str = None, limit: int = 100, offset: int = None) -> List[Dict[str, Any]]:
        with self._session_scope() as session:
            stmt = select(PrescriptionORM)
            conditions = []
            if start_date:
                conditions.append(func.date(PrescriptionORM.created_at) >= start_date)
            if end_date:
                conditions.append(func.date(PrescriptionORM.created_at) <= end_date)
            if patient_name:
                conditions.append(PrescriptionORM.patient_name.like(f'%{patient_name}%'))
            if conditions:
                stmt = stmt.where(and_(*conditions))
            stmt = stmt.order_by(PrescriptionORM.created_at.desc()).limit(limit)
            if offset is not None:
                stmt = stmt.offset(offset)
            rows = session.execute(stmt).scalars().all()
            return [self._orm_to_dict(p) for p in rows]

    def count_all(self, start_date: str = None, end_date: str = None,
                  patient_name: str = None) -> int:
        """统计满足筛选条件的处方总数（用于分页）"""
        with self._session_scope() as session:
            stmt = select(func.count(PrescriptionORM.id))
            conditions = []
            if start_date:
                conditions.append(func.date(PrescriptionORM.created_at) >= start_date)
            if end_date:
                conditions.append(func.date(PrescriptionORM.created_at) <= end_date)
            if patient_name:
                conditions.append(PrescriptionORM.patient_name.like(f'%{patient_name}%'))
            if conditions:
                stmt = stmt.where(and_(*conditions))
            return session.execute(stmt).scalar() or 0

    def get_statistics(self, start_date: str = None, end_date: str = None) -> Dict[str, Any]:
        with self._session_scope() as session:
            stmt = select(
                func.count(PrescriptionORM.id).label('count'),
                func.coalesce(func.sum(PrescriptionORM.total_amount), 0).label('total_amount'),
            )
            conditions = []
            if start_date:
                conditions.append(func.date(PrescriptionORM.created_at) >= start_date)
            if end_date:
                conditions.append(func.date(PrescriptionORM.created_at) <= end_date)
            if conditions:
                stmt = stmt.where(and_(*conditions))
            row = session.execute(stmt).first()
            if not row:
                return {'prescription_count': 0, 'total_amount': 0}
            return {
                'prescription_count': row.count or 0,
                'total_amount': row.total_amount or 0,
            }

    # ====================================================================
    # 写方法（保留 SQL，等阶段 2.4 统一切换）
    # ====================================================================
    def insert_prescription(self, prescription) -> int:
        """插入处方主表，返回处方 id（不含 items）。"""
        from datetime import datetime
        now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        cursor = self.execute(
            '''INSERT INTO prescriptions
               (patient_name, patient_age, patient_gender, diagnosis, total_amount, created_by, created_at)
               VALUES (?, ?, ?, ?, ?, ?, ?)''',
            (prescription.patient_name, prescription.patient_age,
             prescription.patient_gender, prescription.diagnosis,
             prescription.total_amount, prescription.created_by, now)
        )
        return cursor.lastrowid

    def insert_item(self, item) -> None:
        self.execute(
            '''INSERT INTO prescription_items
               (prescription_id, medicine_id, medicine_name, quantity, unit, price, amount)
               VALUES (?, ?, ?, ?, ?, ?, ?)''',
            (item.prescription_id, item.medicine_id, item.medicine_name,
             item.quantity, item.unit, item.price, item.amount)
        )

    def delete_items_by_prescription(self, prescription_id: int) -> None:
        self.execute(
            'DELETE FROM prescription_items WHERE prescription_id = ?',
            (prescription_id,)
        )

    def delete_by_id(self, prescription_id: int) -> None:
        self.execute(
            'DELETE FROM prescriptions WHERE id = ?',
            (prescription_id,)
        )
