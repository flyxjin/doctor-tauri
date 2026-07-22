# -*- coding: utf-8 -*-
"""
药材数据访问 Repository

从 MedicineService 抽取的全部数据访问操作。
Service 层负责验证、缓存同步、事务编排；本类只做读写。

分层策略（v4.3.0 确认）：
- 只读方法：走 SQLAlchemy ORM（_session_scope），与 ORM 模型一致
- 写方法：保留参数化 SQL，走 sqlite3 cursor
  原因：写方法常出现在 Service 层 `with self.db.transaction()` 中，
  与 OperationLogRepository 等其他 Repository 共享同一 sqlite3 事务。
  若改用独立 ORM session，会破坏跨 Repository 原子性。
  保留 SQL 路径是权衡后的决定，参数化查询已保证 SQL 注入安全。
"""
from datetime import datetime
from typing import Any, Dict, List, Optional

from sqlalchemy import func, or_, select

from ..orm_models import DataVersionORM, InventoryORM, MedicineORM
from .base import BaseRepository


class MedicineRepository(BaseRepository):
    """medicines 表（含 inventory 联查）的数据访问。"""

    # ====================================================================
    # 只读方法（已切换 ORM）
    # ====================================================================
    def find_all(self, category: str = None, keyword: str = None) -> List[Dict[str, Any]]:
        with self._session_scope() as session:
            stmt = (
                select(MedicineORM, InventoryORM)
                .outerjoin(InventoryORM, MedicineORM.id == InventoryORM.medicine_id)
            )
            if category:
                stmt = stmt.where(MedicineORM.category == category)
            if keyword:
                kw = f'%{keyword}%'
                stmt = stmt.where(
                    or_(
                        MedicineORM.name.like(kw),
                        MedicineORM.alias.like(kw),
                        MedicineORM.efficacy.like(kw),
                    )
                )
            stmt = stmt.order_by(MedicineORM.name)
            rows = session.execute(stmt).all()
            return [self._medicine_row_to_dict(med, inv) for med, inv in rows]

    def find_by_id(self, medicine_id: int) -> Optional[Dict[str, Any]]:
        with self._session_scope() as session:
            stmt = (
                select(MedicineORM, InventoryORM)
                .outerjoin(InventoryORM, MedicineORM.id == InventoryORM.medicine_id)
                .where(MedicineORM.id == medicine_id)
            )
            row = session.execute(stmt).first()
            if not row:
                return None
            med, inv = row
            return self._medicine_row_to_dict(med, inv)

    def find_by_name(self, name: str) -> Optional[Dict[str, Any]]:
        with self._session_scope() as session:
            stmt = (
                select(MedicineORM, InventoryORM)
                .outerjoin(InventoryORM, MedicineORM.id == InventoryORM.medicine_id)
                .where(MedicineORM.name == name)
            )
            row = session.execute(stmt).first()
            if not row:
                return None
            med, inv = row
            return self._medicine_row_to_dict(med, inv)

    def search(self, keyword: str, fields: List[str] = None) -> List[Dict[str, Any]]:
        if not keyword:
            return []
        if fields is None:
            fields = ['name', 'alias', 'efficacy', 'indications']

        allowed_map = {
            'name': MedicineORM.name,
            'alias': MedicineORM.alias,
            'efficacy': MedicineORM.efficacy,
            'indications': MedicineORM.indications,
            'category': MedicineORM.category,
            'nature': MedicineORM.nature,
            'taste': MedicineORM.taste,
        }
        conditions = []
        for f in fields:
            col = allowed_map.get(f)
            if col is not None:
                conditions.append(col.like(f'%{keyword}%'))
        if not conditions:
            return []

        with self._session_scope() as session:
            stmt = (
                select(MedicineORM, InventoryORM)
                .outerjoin(InventoryORM, MedicineORM.id == InventoryORM.medicine_id)
                .where(or_(*conditions))
                .order_by(MedicineORM.name)
            )
            rows = session.execute(stmt).all()
            return [self._medicine_row_to_dict(med, inv) for med, inv in rows]

    def find_categories(self) -> List[str]:
        with self._session_scope() as session:
            stmt = (
                select(MedicineORM.category)
                .where(MedicineORM.category.isnot(None))
                .distinct()
                .order_by(MedicineORM.category)
            )
            return [row[0] for row in session.execute(stmt).all()]

    def find_all_as_dicts(self) -> List[Dict[str, Any]]:
        """供缓存初始化使用，返回去 None 的字典列表。"""
        with self._session_scope() as session:
            stmt = select(MedicineORM).order_by(MedicineORM.id)
            meds = session.execute(stmt).scalars().all()
            return [self._medicine_to_cache_dict(m) for m in meds]

    # ---- 数据装载专用只读 ----
    def find_id_by_name(self, name: str) -> Optional[int]:
        with self._session_scope() as session:
            stmt = select(MedicineORM.id).where(MedicineORM.name == name)
            row = session.execute(stmt).first()
            return row[0] if row else None

    def find_latest_data_version(self) -> Optional[Dict[str, Any]]:
        with self._session_scope() as session:
            stmt = (
                select(DataVersionORM)
                .order_by(DataVersionORM.created_at.desc())
                .limit(1)
            )
            dv = session.execute(stmt).scalars().first()
            return self._orm_to_dict(dv) if dv else None

    def count_medicines(self) -> int:
        with self._session_scope() as session:
            return session.execute(select(func.count(MedicineORM.id))).scalar() or 0

    def find_medicines_without_inventory(self) -> List[Dict[str, Any]]:
        with self._session_scope() as session:
            stmt = (
                select(MedicineORM.name)
                .outerjoin(InventoryORM, MedicineORM.id == InventoryORM.medicine_id)
                .where(InventoryORM.id.is_(None))
            )
            return [{'name': row[0]} for row in session.execute(stmt).all()]

    def find_orphan_inventory(self) -> List[Dict[str, Any]]:
        with self._session_scope() as session:
            stmt = (
                select(InventoryORM.medicine_id)
                .outerjoin(MedicineORM, InventoryORM.medicine_id == MedicineORM.id)
                .where(MedicineORM.id.is_(None))
            )
            return [{'medicine_id': row[0]} for row in session.execute(stmt).all()]

    # ---- 处方开具页专用只读（替代 prescription_view 直接查 medicines 表） ----
    def find_medicines_with_stock(self, keyword: str = None, limit: int = 200) -> List[Dict[str, Any]]:
        """药材搜索（含库存信息），用于处方开具页"""
        with self._session_scope() as session:
            stmt = (
                select(
                    MedicineORM.name.label('name'),
                    InventoryORM.price.label('price'),
                    InventoryORM.quantity.label('quantity'),
                )
                .outerjoin(InventoryORM, MedicineORM.id == InventoryORM.medicine_id)
            )
            if keyword:
                kw = f'%{keyword}%'
                stmt = stmt.where(
                    (MedicineORM.name.like(kw)) | (MedicineORM.alias.like(kw))
                )
            stmt = stmt.order_by(MedicineORM.name).limit(limit)
            return [dict(row._mapping) for row in session.execute(stmt).all()]

    def find_medicine_detail_for_prescription(self, name: str) -> Optional[Dict[str, Any]]:
        """查处方添加用的药材详情（id/价格/库存/禁忌）"""
        with self._session_scope() as session:
            stmt = (
                select(
                    MedicineORM.id.label('id'),
                    InventoryORM.price.label('price'),
                    InventoryORM.quantity.label('quantity'),
                    MedicineORM.contraindication.label('contraindication'),
                )
                .join(InventoryORM, MedicineORM.id == InventoryORM.medicine_id)
                .where(MedicineORM.name == name)
            )
            row = session.execute(stmt).first()
            return dict(row._mapping) if row else None

    # ====================================================================
    # 写方法（保留参数化 SQL，走 sqlite3 事务）
    # 原因：这些方法常出现在 Service 层 with self.db.transaction() 中，
    #       与其他 Repository（如 OperationLog）的 SQL 操作共享同一 sqlite3 事务。
    #       若内部改用独立 ORM session，会破坏跨 Repository 原子性。
    #       参数化查询已保证 SQL 注入安全；事务边界由 Service 层控制。
    # ====================================================================
    def insert_medicine(self, medicine) -> int:
        """插入药材并初始化库存记录，返回新药材 id。"""
        query = '''
            INSERT INTO medicines (name, alias, category, nature, taste, meridian,
                                   efficacy, indications, usage, dosage, contraindication, notes)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        '''
        params = (
            medicine.name, medicine.alias, medicine.category, medicine.nature,
            medicine.taste, medicine.meridian, medicine.efficacy, medicine.indications,
            medicine.usage, medicine.dosage, medicine.contraindication, medicine.notes
        )
        cursor = self.execute(query, params)
        medicine_id = cursor.lastrowid

        self.execute(
            '''INSERT INTO inventory (medicine_id, quantity, unit, price, min_stock, notes)
               VALUES (?, 0, 'g', 0, 0, '')''',
            (medicine_id,)
        )
        return medicine_id

    def update_medicine(self, medicine) -> None:
        query = '''
            UPDATE medicines SET name=?, alias=?, category=?, nature=?, taste=?,
                                  meridian=?, efficacy=?, indications=?, usage=?,
                                  dosage=?, contraindication=?, notes=?, updated_at=CURRENT_TIMESTAMP
            WHERE id=?
        '''
        self.execute(query, (
            medicine.name, medicine.alias, medicine.category, medicine.nature,
            medicine.taste, medicine.meridian, medicine.efficacy, medicine.indications,
            medicine.usage, medicine.dosage, medicine.contraindication, medicine.notes,
            medicine.id
        ))

    def delete_by_id(self, medicine_id: int) -> None:
        """级联删除药材相关数据。调用方需在事务中调用。"""
        self.execute('DELETE FROM inventory_history WHERE medicine_id = ?', (medicine_id,))
        self.execute('DELETE FROM prescription_items WHERE medicine_id = ?', (medicine_id,))
        self.execute('DELETE FROM inventory WHERE medicine_id = ?', (medicine_id,))
        self.execute('DELETE FROM medicines WHERE id = ?', (medicine_id,))

    # ---- 数据装载专用写（dict 输入，含库存） ----
    def insert_with_inventory(self, item: Dict[str, Any]) -> int:
        """从 dict 插入药材+库存（用于批量导入/数据装载），返回新 id。"""
        cursor = self.execute(
            '''INSERT INTO medicines
               (name, alias, category, nature, taste, meridian,
                efficacy, indications, usage, dosage, contraindication, notes)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
            (item.get('name', ''), item.get('alias', ''), item.get('category', ''),
             item.get('nature', ''), item.get('taste', ''), item.get('meridian', ''),
             item.get('efficacy', ''), item.get('indications', ''), item.get('usage', ''),
             item.get('dosage', ''), item.get('contraindication', ''), item.get('notes', ''))
        )
        medicine_id = cursor.lastrowid
        self.execute(
            '''INSERT INTO inventory (medicine_id, quantity, unit, price, min_stock, notes)
               VALUES (?, ?, ?, ?, ?, ?)''',
            (medicine_id, item.get('quantity', 0), item.get('unit', 'g'),
             item.get('price', 0), item.get('min_stock', 0), item.get('notes', ''))
        )
        return medicine_id

    def update_with_inventory(self, medicine_id: int, item: Dict[str, Any]) -> None:
        """从 dict 更新药材+库存（用于批量导入/数据装载）。
        若 inventory 记录缺失则自动补建，确保 medicines 与 inventory 一致。"""
        self.execute(
            '''UPDATE medicines SET alias=?, category=?, nature=?, taste=?, meridian=?,
                                      efficacy=?, indications=?, usage=?, dosage=?,
                                      contraindication=?, notes=?, updated_at=CURRENT_TIMESTAMP
               WHERE id=?''',
            (item.get('alias', ''), item.get('category', ''), item.get('nature', ''),
             item.get('taste', ''), item.get('meridian', ''), item.get('efficacy', ''),
             item.get('indications', ''), item.get('usage', ''), item.get('dosage', ''),
             item.get('contraindication', ''), item.get('notes', ''), medicine_id)
        )
        # UPSERT：先查 inventory 是否存在，不存在则 INSERT，存在则 UPDATE
        existing = self.fetchone(
            'SELECT medicine_id FROM inventory WHERE medicine_id = ?',
            (medicine_id,)
        )
        if existing:
            self.execute(
                '''UPDATE inventory SET quantity=?, unit=?, price=?, min_stock=?, updated_at=CURRENT_TIMESTAMP
                   WHERE medicine_id=?''',
                (item.get('quantity', 0), item.get('unit', 'g'), item.get('price', 0),
                 item.get('min_stock', 0), medicine_id)
            )
        else:
            # 补建缺失的 inventory 记录
            self.execute(
                '''INSERT INTO inventory (medicine_id, quantity, unit, price, min_stock, notes)
                   VALUES (?, ?, ?, ?, ?, ?)''',
                (medicine_id, item.get('quantity', 0), item.get('unit', 'g'),
                 item.get('price', 0), item.get('min_stock', 0), item.get('notes', ''))
            )

    def record_data_version(self, medicine_count: int, checksum: str) -> None:
        version = datetime.now().strftime('%Y%m%d%H%M%S')
        self.execute(
            '''INSERT INTO data_version (version, medicine_count, checksum)
               VALUES (?, ?, ?)''',
            (version, medicine_count, checksum)
        )

    # ====================================================================
    # ORM → dict 转换辅助
    # ====================================================================
    @staticmethod
    def _medicine_row_to_dict(med: MedicineORM, inv: Optional[InventoryORM]) -> Dict[str, Any]:
        """将 medicines LEFT JOIN inventory 的查询结果转为 dict。"""
        d = {
            'id': med.id,
            'name': med.name or '',
            'alias': med.alias or '',
            'category': med.category or '',
            'nature': med.nature or '',
            'taste': med.taste or '',
            'meridian': med.meridian or '',
            'efficacy': med.efficacy or '',
            'indications': med.indications or '',
            'usage': med.usage or '',
            'dosage': med.dosage or '',
            'contraindication': med.contraindication or '',
            'notes': med.notes or '',
            'created_at': med.created_at,
            'updated_at': med.updated_at,
        }
        if inv is not None:
            d.update({
                'quantity': inv.quantity,
                'unit': inv.unit,
                'price': inv.price,
                'min_stock': inv.min_stock,
            })
        return d

    @staticmethod
    def _medicine_to_cache_dict(med: MedicineORM) -> Dict[str, Any]:
        """缓存初始化专用：去 None，只含 medicines 表字段。"""
        return {
            'id': med.id,
            'name': med.name or '',
            'alias': med.alias or '',
            'category': med.category or '',
            'nature': med.nature or '',
            'taste': med.taste or '',
            'meridian': med.meridian or '',
            'efficacy': med.efficacy or '',
            'indications': med.indications or '',
            'usage': med.usage or '',
            'dosage': med.dosage or '',
            'contraindication': med.contraindication or '',
            'notes': med.notes or '',
        }
