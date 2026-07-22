# -*- coding: utf-8 -*-
"""
库存数据访问 Repository

从 InventoryService 抽取的全部数据访问操作（含 inventory_history）。

阶段 2.3：只读方法切换到 SQLAlchemy ORM；写方法保留 SQL（等阶段 2.4 统一切换）。
"""
from typing import Any, Dict, List, Optional

from sqlalchemy import select

from ..orm_models import InventoryHistoryORM, InventoryORM, MedicineORM
from .base import BaseRepository


class InventoryRepository(BaseRepository):
    """inventory 与 inventory_history 表的数据访问。"""

    # ====================================================================
    # 只读方法（已切换 ORM）
    # ====================================================================
    def find_all(self, low_stock_only: bool = False, keyword: str = None,
                 stock_status: str = None) -> List[Dict[str, Any]]:
        with self._session_scope() as session:
            stmt = (
                select(InventoryORM, MedicineORM.name.label('medicine_name'),
                       MedicineORM.category)
                .join(MedicineORM, InventoryORM.medicine_id == MedicineORM.id)
            )
            if keyword:
                stmt = stmt.where(MedicineORM.name.like(f'%{keyword}%'))

            if low_stock_only:
                stmt = stmt.where(InventoryORM.quantity <= InventoryORM.min_stock)
            elif stock_status:
                if stock_status == '库存充足':
                    stmt = stmt.where(InventoryORM.quantity >= InventoryORM.min_stock)
                elif stock_status == '低库存':
                    stmt = stmt.where(
                        (InventoryORM.quantity > 0)
                        & (InventoryORM.quantity < InventoryORM.min_stock)
                    )
                elif stock_status == '缺货':
                    stmt = stmt.where(InventoryORM.quantity == 0)

            stmt = stmt.order_by(MedicineORM.name)
            rows = session.execute(stmt).all()
            return [self._inventory_row_to_dict(inv, row.medicine_name, row.category)
                    for row in rows for inv in [row[0]]]

    def find_by_medicine_id(self, medicine_id: int) -> Optional[Dict[str, Any]]:
        with self._session_scope() as session:
            stmt = (
                select(InventoryORM, MedicineORM.name.label('medicine_name'))
                .join(MedicineORM, InventoryORM.medicine_id == MedicineORM.id)
                .where(InventoryORM.medicine_id == medicine_id)
            )
            row = session.execute(stmt).first()
            if not row:
                return None
            return self._inventory_row_to_dict(row[0], row.medicine_name, None)

    def find_history(self, medicine_id: int = None, limit: int = 100) -> List[Dict[str, Any]]:
        with self._session_scope() as session:
            stmt = select(InventoryHistoryORM)
            if medicine_id:
                stmt = stmt.where(InventoryHistoryORM.medicine_id == medicine_id)
            stmt = stmt.order_by(InventoryHistoryORM.created_at.desc()).limit(limit)
            rows = session.execute(stmt).scalars().all()
            return [self._orm_to_dict(h) for h in rows]

    # ====================================================================
    # 写方法（保留 SQL，等阶段 2.4 统一切换）
    # ====================================================================
    def update_stock(self, medicine_id: int, new_quantity: float,
                     price: float = None) -> None:
        """更新库存数量，可选更新单价。"""
        if price is not None:
            self.execute(
                '''UPDATE inventory SET quantity = ?, price = ?, updated_at = CURRENT_TIMESTAMP
                   WHERE medicine_id = ?''',
                (new_quantity, price, medicine_id)
            )
        else:
            self.execute(
                '''UPDATE inventory SET quantity = ?, updated_at = CURRENT_TIMESTAMP
                   WHERE medicine_id = ?''',
                (new_quantity, medicine_id)
            )

    def update_price(self, medicine_id: int, price: float) -> None:
        self.execute(
            'UPDATE inventory SET price = ?, updated_at = CURRENT_TIMESTAMP WHERE medicine_id = ?',
            (price, medicine_id)
        )

    def update_min_stock(self, medicine_id: int, min_stock: float) -> None:
        self.execute(
            'UPDATE inventory SET min_stock = ?, updated_at = CURRENT_TIMESTAMP WHERE medicine_id = ?',
            (min_stock, medicine_id)
        )

    def adjust_stock(self, medicine_id: int, new_quantity: float,
                     price: float = None, min_stock: float = None) -> None:
        """调整库存（绝对值），可选同时更新单价/最低库存。"""
        query = 'UPDATE inventory SET quantity = ?'
        params: List[Any] = [new_quantity]

        if price is not None:
            query += ', price = ?'
            params.append(price)
        if min_stock is not None:
            query += ', min_stock = ?'
            params.append(min_stock)

        query += ', updated_at = CURRENT_TIMESTAMP WHERE medicine_id = ?'
        params.append(medicine_id)
        self.execute(query, tuple(params))

    # ---- inventory_history ----
    def insert_history(self, medicine_id: int, medicine_name: str, type_: str,
                       quantity: float, price: float = None, total_amount: float = None,
                       operator: str = '', notes: str = '') -> None:
        self.execute(
            '''INSERT INTO inventory_history
               (medicine_id, medicine_name, type, quantity, price, total_amount, operator, notes)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?)''',
            (medicine_id, medicine_name, type_, quantity, price, total_amount, operator, notes)
        )

    # ====================================================================
    # ORM → dict 转换辅助
    # ====================================================================
    @staticmethod
    def _inventory_row_to_dict(inv: InventoryORM, medicine_name: str,
                               category: Optional[str]) -> Dict[str, Any]:
        """将 inventory JOIN medicines 的查询结果转为 dict。"""
        d = {c.key: getattr(inv, c.key) for c in inv.__table__.columns}
        d['medicine_name'] = medicine_name or ''
        if category is not None:
            d['category'] = category or ''
        return d
