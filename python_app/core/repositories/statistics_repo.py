# -*- coding: utf-8 -*-
"""
统计分析数据访问 Repository

收纳 dashboard_view 与 statistics_view 中散落的 SQL 查询，统一数据访问入口。
解决 v3.1.0 之后遗留的"View 直接 db.fetchall 绕过 Service/Repository"分层破口。

阶段 2.3：全部走 SQLAlchemy ORM。
"""
from datetime import datetime
from typing import Any, Dict, List

from sqlalchemy import desc, func, select

from ..orm_models import (
    InventoryORM,
    MedicineORM,
    PrescriptionItemORM,
    PrescriptionORM,
)
from .base import BaseRepository


class StatisticsRepository(BaseRepository):
    """仪表盘与销售统计相关的聚合查询。"""

    # ====================================================================
    # 仪表盘（Dashboard）相关查询
    # ====================================================================
    def find_today_summary(self, start_dt: datetime, end_dt: datetime) -> Dict[str, Any]:
        """今日处方数与营收汇总"""
        with self._session_scope() as session:
            stmt = select(
                func.count(PrescriptionORM.id).label('cnt'),
                func.coalesce(func.sum(PrescriptionORM.total_amount), 0).label('revenue'),
            ).where(
                PrescriptionORM.created_at.between(
                    start_dt.strftime('%Y-%m-%d %H:%M:%S'),
                    end_dt.strftime('%Y-%m-%d %H:%M:%S'),
                )
            )
            row = session.execute(stmt).first()
            if not row:
                return {'cnt': 0, 'revenue': 0}
            return {'cnt': row.cnt or 0, 'revenue': float(row.revenue or 0)}

    def count_medicines(self) -> int:
        """药材总数"""
        with self._session_scope() as session:
            return session.execute(select(func.count(MedicineORM.id))).scalar() or 0

    def find_low_stock_alerts(self, limit: int = 10) -> List[Dict[str, Any]]:
        """低库存预警列表（按库存升序）"""
        with self._session_scope() as session:
            stmt = (
                select(
                    MedicineORM.name.label('name'),
                    InventoryORM.quantity.label('quantity'),
                    InventoryORM.min_stock.label('min_stock'),
                )
                .join(InventoryORM, MedicineORM.id == InventoryORM.medicine_id)
                .where(InventoryORM.quantity <= InventoryORM.min_stock)
                .order_by(InventoryORM.quantity.asc())
                .limit(limit)
            )
            return [dict(row._mapping) for row in session.execute(stmt).all()]

    def find_recent_prescriptions(self, limit: int = 5) -> List[Dict[str, Any]]:
        """最近处方列表"""
        with self._session_scope() as session:
            stmt = (
                select(
                    PrescriptionORM.id.label('id'),
                    PrescriptionORM.patient_name.label('patient_name'),
                    PrescriptionORM.total_amount.label('total_amount'),
                    PrescriptionORM.created_at.label('created_at'),
                )
                .order_by(PrescriptionORM.created_at.desc())
                .limit(limit)
            )
            return [dict(row._mapping) for row in session.execute(stmt).all()]

    def find_revenue_trend_7_days(self, start_date: str, end_date: str) -> List[Dict[str, Any]]:
        """近 7 天营收趋势（按日期分组）"""
        with self._session_scope() as session:
            stmt = (
                select(
                    func.date(PrescriptionORM.created_at).label('date'),
                    func.coalesce(func.sum(PrescriptionORM.total_amount), 0).label('revenue'),
                )
                .where(PrescriptionORM.created_at.between(start_date, end_date))
                .group_by(func.date(PrescriptionORM.created_at))
                .order_by(func.date(PrescriptionORM.created_at).asc())
            )
            return [dict(row._mapping) for row in session.execute(stmt).all()]

    # ====================================================================
    # 销售统计（Statistics）相关查询
    # ====================================================================
    def find_prescription_summary(self, start_date: str, end_date: str) -> Dict[str, Any]:
        """指定时间范围内处方数与营收汇总"""
        with self._session_scope() as session:
            stmt = select(
                func.count(PrescriptionORM.id).label('cnt'),
                func.coalesce(func.sum(PrescriptionORM.total_amount), 0).label('revenue'),
            ).where(PrescriptionORM.created_at.between(start_date, end_date))
            row = session.execute(stmt).first()
            if not row:
                return {'cnt': 0, 'revenue': 0}
            return {'cnt': row.cnt or 0, 'revenue': float(row.revenue or 0)}

    def count_low_stock(self) -> int:
        """低库存药材数量"""
        with self._session_scope() as session:
            stmt = select(func.count(InventoryORM.id)).where(
                InventoryORM.quantity <= InventoryORM.min_stock
            )
            return session.execute(stmt).scalar() or 0

    def find_top_medicines(self, start_date: str, end_date: str, limit: int = 10) -> List[Dict[str, Any]]:
        """热销药材 TOP N"""
        with self._session_scope() as session:
            stmt = (
                select(
                    PrescriptionItemORM.medicine_name.label('name'),
                    func.count().label('freq'),
                    func.coalesce(func.sum(PrescriptionItemORM.quantity), 0).label('total_qty'),
                )
                .join(PrescriptionORM, PrescriptionItemORM.prescription_id == PrescriptionORM.id)
                .where(PrescriptionORM.created_at.between(start_date, end_date))
                .group_by(PrescriptionItemORM.medicine_name)
                .order_by(desc(func.count()))
                .limit(limit)
            )
            return [dict(row._mapping) for row in session.execute(stmt).all()]

    def find_revenue_trend(self, start_date: str, end_date: str, limit: int = 30) -> List[Dict[str, Any]]:
        """营收趋势（按日期分组，倒序）"""
        with self._session_scope() as session:
            stmt = (
                select(
                    func.date(PrescriptionORM.created_at).label('date'),
                    func.count().label('cnt'),
                    func.coalesce(func.sum(PrescriptionORM.total_amount), 0).label('revenue'),
                )
                .where(PrescriptionORM.created_at.between(start_date, end_date))
                .group_by(func.date(PrescriptionORM.created_at))
                .order_by(desc(func.date(PrescriptionORM.created_at)))
                .limit(limit)
            )
            return [dict(row._mapping) for row in session.execute(stmt).all()]
