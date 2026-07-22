# -*- coding: utf-8 -*-
"""
患者档案数据访问 Repository

负责 patients 表的 CRUD，以及通过 patient.name 关联 prescriptions 表查询
患者的处方历史与统计数据。

分层策略（与 medicine_repo 一致）：
- 只读方法：走 SQLAlchemy ORM（_session_scope），与 ORM 模型一致
- 写方法：保留参数化 SQL，走 sqlite3 cursor
  原因：写方法常出现在 Service 层 `with self.db.transaction()` 中，
  与 OperationLogRepository 等其他 Repository 共享同一 sqlite3 事务。
  若改用独立 ORM session，会破坏跨 Repository 原子性。
  保留 SQL 路径是权衡后的决定，参数化查询已保证 SQL 注入安全。
"""
from typing import Any, Dict, List, Optional

from sqlalchemy import func, or_, select

from ..orm_models import PatientORM, PrescriptionORM
from .base import BaseRepository


class PatientRepository(BaseRepository):
    """patients 表的数据访问，并关联 prescriptions 表提供患者历史视图。"""

    # ====================================================================
    # 只读方法（走 ORM）
    # ====================================================================
    def find_by_id(self, patient_id: int) -> Optional[Dict[str, Any]]:
        with self._session_scope() as session:
            stmt = select(PatientORM).where(PatientORM.id == patient_id)
            p = session.execute(stmt).scalars().first()
            return self._orm_to_dict(p) if p else None

    def find_all(self, keyword: str = "") -> List[Dict[str, Any]]:
        """查询所有患者（支持按姓名/电话模糊搜索）"""
        with self._session_scope() as session:
            stmt = select(PatientORM)
            if keyword:
                kw = f'%{keyword}%'
                stmt = stmt.where(
                    or_(
                        PatientORM.name.like(kw),
                        PatientORM.phone.like(kw),
                    )
                )
            stmt = stmt.order_by(PatientORM.created_at.desc())
            rows = session.execute(stmt).scalars().all()
            return [self._orm_to_dict(p) for p in rows]

    def find_by_name(self, name: str) -> Optional[Dict[str, Any]]:
        """按姓名精确查询（返回第一条匹配，调用方需自行处理同名场景）"""
        with self._session_scope() as session:
            stmt = (
                select(PatientORM)
                .where(PatientORM.name == name)
                .order_by(PatientORM.id.asc())
                .limit(1)
            )
            p = session.execute(stmt).scalars().first()
            return self._orm_to_dict(p) if p else None

    def find_prescriptions_by_name(self, name: str) -> List[Dict[str, Any]]:
        """通过 patient_name 关联 prescriptions 表，查询患者处方历史。"""
        with self._session_scope() as session:
            stmt = (
                select(
                    PrescriptionORM.id.label('prescription_id'),
                    PrescriptionORM.patient_name.label('patient_name'),
                    PrescriptionORM.patient_age.label('patient_age'),
                    PrescriptionORM.patient_gender.label('patient_gender'),
                    PrescriptionORM.diagnosis.label('diagnosis'),
                    PrescriptionORM.total_amount.label('total_amount'),
                    PrescriptionORM.created_by.label('created_by'),
                    PrescriptionORM.created_at.label('created_at'),
                )
                .where(PrescriptionORM.patient_name == name)
                .order_by(PrescriptionORM.created_at.desc())
            )
            return [dict(row._mapping) for row in session.execute(stmt).all()]

    def find_statistics_by_name(self, name: str) -> Dict[str, Any]:
        """按姓名统计患者的处方数、总消费、首次就诊、最近就诊。"""
        with self._session_scope() as session:
            stmt = select(
                func.count(PrescriptionORM.id).label('prescription_count'),
                func.coalesce(func.sum(PrescriptionORM.total_amount), 0).label('total_amount'),
                func.min(PrescriptionORM.created_at).label('first_visit'),
                func.max(PrescriptionORM.created_at).label('last_visit'),
            ).where(PrescriptionORM.patient_name == name)
            row = session.execute(stmt).first()
            if not row:
                return {
                    'prescription_count': 0,
                    'total_amount': 0.0,
                    'first_visit': None,
                    'last_visit': None,
                }
            return {
                'prescription_count': row.prescription_count or 0,
                'total_amount': float(row.total_amount or 0),
                'first_visit': row.first_visit,
                'last_visit': row.last_visit,
            }

    # ====================================================================
    # 写方法（保留参数化 SQL，走 sqlite3 事务）
    # 原因：与 medicine_repo 保持一致，写方法常出现在 Service 层
    #       with self.db.transaction() 中，与其他 Repository 共享事务。
    # ====================================================================
    def insert_patient(self, patient) -> int:
        """插入患者档案，返回新患者 id。"""
        cursor = self.execute(
            '''INSERT INTO patients
               (name, gender, age, phone, address, allergy, medical_history, notes)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?)''',
            (patient.name, patient.gender, patient.age, patient.phone,
             patient.address, patient.allergy, patient.medical_history, patient.notes)
        )
        return cursor.lastrowid

    def update_patient(self, patient) -> None:
        self.execute(
            '''UPDATE patients SET name=?, gender=?, age=?, phone=?, address=?,
                                   allergy=?, medical_history=?, notes=?,
                                   updated_at=datetime('now','localtime')
               WHERE id=?''',
            (patient.name, patient.gender, patient.age, patient.phone,
             patient.address, patient.allergy, patient.medical_history,
             patient.notes, patient.id)
        )

    def delete_by_id(self, patient_id: int) -> None:
        """删除患者档案。注意：不级联删除 prescriptions，处方记录独立保留。"""
        self.execute('DELETE FROM patients WHERE id = ?', (patient_id,))
