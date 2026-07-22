# -*- coding: utf-8 -*-
"""
服务层 - 业务逻辑处理
"""
import hashlib
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Tuple

from .cache import get_medicine_cache
from .database import Database
from .models import Inventory, InventoryHistory, Medicine, Patient, Prescription, PrescriptionItem
from .validators import MedicineValidator


def _sync_cache_add(medicine: Medicine, medicine_id: int) -> None:
    """创建药材后同步添加到缓存（缓存未初始化时跳过）"""
    import logging
    cache = get_medicine_cache()
    if not cache.is_initialized():
        return
    try:
        medicine.id = medicine_id
        medicine_dict = medicine.to_dict()
        medicine_dict.update({
            'quantity': 0, 'unit': 'g', 'price': 0, 'min_stock': 0, 'notes': ''
        })
        cache.add_medicine(medicine_dict)
    except Exception as e:
        logging.getLogger('MedicineSystem').warning(f"缓存同步(新增)失败: {e}")


def _sync_cache_update(medicine: Medicine) -> None:
    """更新药材后同步刷新缓存（缓存未初始化时跳过）"""
    import logging
    cache = get_medicine_cache()
    if not cache.is_initialized():
        return
    try:
        # 重新查询带库存的完整数据
        row = Database().fetchone(
            '''SELECT m.*, i.quantity, i.unit, i.price, i.min_stock
               FROM medicines m LEFT JOIN inventory i ON m.id = i.medicine_id
               WHERE m.id = ?''',
            (medicine.id,)
        )
        if row:
            cache.update_medicine(dict(row))
    except Exception as e:
        logging.getLogger('MedicineSystem').warning(f"缓存同步(更新)失败: {e}")


def _sync_cache_delete(medicine_id: int) -> None:
    """删除药材后同步从缓存移除（缓存未初始化时跳过）"""
    import logging
    cache = get_medicine_cache()
    if not cache.is_initialized():
        return
    try:
        cache.delete_medicine(medicine_id)
    except Exception as e:
        logging.getLogger('MedicineSystem').warning(f"缓存同步(删除)失败: {e}")


class ServiceError(Exception):
    pass


def _log_operation(db, operation_type: str, target_type: str, target_id: int, details: str = ''):
    """记录操作日志。委托给 OperationLogRepository，保留原签名以兼容调用点。"""
    from core.repositories import OperationLogRepository
    OperationLogRepository(db).insert(operation_type, target_type, target_id, details)


class MedicineService:
    def __init__(self, db: Database = None):
        self.db = db or Database()
        from core.repositories import MedicineRepository
        self._repo = MedicineRepository(self.db)

    def get_all(self, category: str = None, keyword: str = None) -> List[Medicine]:
        rows = self._repo.find_all(category=category, keyword=keyword)
        return [Medicine.from_dict(row) for row in rows]

    def get_by_id(self, medicine_id: int) -> Optional[Medicine]:
        row = self._repo.find_by_id(medicine_id)
        return Medicine.from_dict(row) if row else None

    def get_by_name(self, name: str) -> Optional[Medicine]:
        row = self._repo.find_by_name(name)
        return Medicine.from_dict(row) if row else None

    def create(self, medicine: Medicine) -> int:
        is_valid, errors = MedicineValidator.validate(medicine.to_dict())
        if not is_valid:
            raise ServiceError(f"数据验证失败: {', '.join(errors)}")

        existing = self.get_by_name(medicine.name)
        if existing:
            raise ServiceError(f"药材 '{medicine.name}' 已存在")

        try:
            with self.db.transaction():
                medicine_id = self._repo.insert_medicine(medicine)
                _log_operation(self.db, 'CREATE', 'medicine', medicine_id, f"创建药材: {medicine.name}")
        except Exception as e:
            raise ServiceError(f"创建药材失败: {e}")

        _sync_cache_add(medicine, medicine_id)
        return medicine_id

    def update(self, medicine: Medicine) -> bool:
        if not medicine.id:
            raise ServiceError("药材ID不能为空")

        is_valid, errors = MedicineValidator.validate(medicine.to_dict())
        if not is_valid:
            raise ServiceError(f"数据验证失败: {', '.join(errors)}")

        existing = self.get_by_name(medicine.name)
        if existing and existing.id != medicine.id:
            raise ServiceError(f"药材名称 '{medicine.name}' 已被其他药材使用")

        try:
            with self.db.transaction():
                self._repo.update_medicine(medicine)
                _log_operation(self.db, 'UPDATE', 'medicine', medicine.id, f"更新药材: {medicine.name}")
        except Exception as e:
            raise ServiceError(f"更新药材失败: {e}")

        _sync_cache_update(medicine)
        return True

    def delete(self, medicine_id: int) -> bool:
        medicine = self.get_by_id(medicine_id)
        if not medicine:
            raise ServiceError("药材不存在")

        try:
            with self.db.transaction():
                self._repo.delete_by_id(medicine_id)
                _log_operation(self.db, 'DELETE', 'medicine', medicine_id, f"删除药材: {medicine.name}")
        except Exception as e:
            raise ServiceError(f"删除药材失败: {e}")

        _sync_cache_delete(medicine_id)
        return True

    def get_categories(self) -> List[str]:
        return self._repo.find_categories()

    def search(self, keyword: str, fields: List[str] = None) -> List[Medicine]:
        rows = self._repo.search(keyword, fields)
        return [Medicine.from_dict(row) for row in rows]

    def get_all_as_dicts(self) -> List[Dict[str, Any]]:
        return self._repo.find_all_as_dicts()

    def search_with_stock(self, keyword: str = None, limit: int = 200) -> List[Dict[str, Any]]:
        """药材搜索（含库存信息），用于处方开具页"""
        return self._repo.find_medicines_with_stock(keyword, limit)

    def get_detail_for_prescription(self, name: str) -> Optional[Dict[str, Any]]:
        """查处方添加用的药材详情（id/价格/库存/禁忌）"""
        return self._repo.find_medicine_detail_for_prescription(name)


class InventoryService:
    def __init__(self, db: Database = None):
        self.db = db or Database()
        from core.repositories import InventoryRepository
        self._repo = InventoryRepository(self.db)

    def get_all(self, low_stock_only: bool = False, keyword: str = None,
                stock_status: str = None) -> List[Inventory]:
        rows = self._repo.find_all(low_stock_only=low_stock_only,
                                   keyword=keyword, stock_status=stock_status)
        return [Inventory.from_dict(row) for row in rows]

    def get_by_medicine_id(self, medicine_id: int) -> Optional[Inventory]:
        row = self._repo.find_by_medicine_id(medicine_id)
        return Inventory.from_dict(row) if row else None

    def update_stock(self, medicine_id: int, quantity_change: float,
                     operation_type: str, price: float = None,
                     notes: str = '', operator: str = '') -> bool:
        inventory = self.get_by_medicine_id(medicine_id)
        if not inventory:
            raise ServiceError("库存记录不存在")

        new_quantity = inventory.quantity + quantity_change
        if new_quantity < 0:
            raise ServiceError(f"库存不足，当前库存: {inventory.quantity}，需要: {abs(quantity_change)}")

        self._repo.update_stock(medicine_id, new_quantity, price)

        total_amount = None
        if price is not None and quantity_change != 0:
            total_amount = abs(quantity_change) * price

        self._repo.insert_history(
            medicine_id, inventory.medicine_name, operation_type,
            abs(quantity_change), price, total_amount, operator, notes
        )
        return True

    def stock_in(self, medicine_id: int, quantity: float, price: float = None,
                 notes: str = '', operator: str = '') -> bool:
        return self.update_stock(medicine_id, quantity, '入库', price, notes, operator)

    def stock_out(self, medicine_id: int, quantity: float, price: float = None,
                  notes: str = '', operator: str = '') -> bool:
        return self.update_stock(medicine_id, -quantity, '出库', price, notes, operator)

    def get_history(self, medicine_id: int = None, limit: int = 100) -> List[InventoryHistory]:
        rows = self._repo.find_history(medicine_id, limit)
        return [InventoryHistory.from_dict(row) for row in rows]

    def get_low_stock_items(self) -> List[Inventory]:
        return self.get_all(low_stock_only=True)

    def get_summary(self) -> Dict[str, Any]:
        """返回库存汇总：药材种类数（基于 medicines 表，与其他页面一致）、低库存数、库存总值。
        用聚合 SQL 一次完成，避免 InventoryView 重复查询。"""
        med_count_row = self.db.fetchone('SELECT COUNT(*) as cnt FROM medicines') or {'cnt': 0}
        total_count = med_count_row['cnt'] if isinstance(med_count_row, dict) else med_count_row[0]

        agg_row = self.db.fetchone(
            '''SELECT
                   SUM(CASE WHEN quantity <= min_stock THEN 1 ELSE 0 END) as low_stock,
                   COALESCE(SUM(quantity * price), 0) as total_value
               FROM inventory'''
        ) or {'low_stock': 0, 'total_value': 0}
        if isinstance(agg_row, dict):
            low_stock = agg_row.get('low_stock') or 0
            total_value = agg_row.get('total_value') or 0
        else:
            low_stock = agg_row[0] or 0
            total_value = agg_row[1] or 0

        return {
            'total_count': total_count,
            'low_stock_count': int(low_stock),
            'total_value': float(total_value),
        }

    def update_price(self, medicine_id: int, price: float) -> bool:
        self._repo.update_price(medicine_id, price)
        return True

    def update_min_stock(self, medicine_id: int, min_stock: float) -> bool:
        self._repo.update_min_stock(medicine_id, min_stock)
        return True

    def adjust_stock(self, medicine_id: int, new_quantity: float, price: float = None,
                     min_stock: float = None, notes: str = '') -> bool:
        inventory = self.get_by_medicine_id(medicine_id)
        if not inventory:
            raise ServiceError("库存记录不存在")

        self._repo.adjust_stock(medicine_id, new_quantity, price, min_stock)

        self._repo.insert_history(
            medicine_id, inventory.medicine_name, '调整',
            new_quantity, price, new_quantity * (price or 0), '系统', notes
        )
        return True


class PrescriptionService:
    def __init__(self, db: Database = None):
        self.db = db or Database()
        from core.repositories import PrescriptionRepository
        self._repo = PrescriptionRepository(self.db)
        self.medicine_service = MedicineService(db)
        self.inventory_service = InventoryService(db)

    def create(self, prescription: Prescription, items: List[PrescriptionItem]) -> int:
        try:
            with self.db.transaction():
                prescription_id = self._repo.insert_prescription(prescription)

                for item in items:
                    item.prescription_id = prescription_id
                    self._repo.insert_item(item)

                    # 在主事务内通过 SQL 查询当前库存（避免 ORM Session 独立事务读到旧数据）
                    inv_row = self.db.fetchone(
                        'SELECT quantity, price FROM inventory WHERE medicine_id = ?',
                        (item.medicine_id,)
                    )
                    if not inv_row:
                        raise ServiceError(f"药材 ID {item.medicine_id} 缺少库存记录")
                    current_qty = inv_row['quantity'] if isinstance(inv_row, dict) else inv_row[0]
                    if current_qty < item.quantity:
                        raise ServiceError(
                            f"药材 '{item.medicine_name}' 库存不足: 当前 {current_qty}，需要 {item.quantity}"
                        )

                    # 直接在主事务内扣减库存、写历史，避免跨 Service 事务隔离问题
                    new_qty = current_qty - item.quantity
                    self.db.execute(
                        'UPDATE inventory SET quantity = ? WHERE medicine_id = ?',
                        (new_qty, item.medicine_id)
                    )
                    self.db.execute(
                        '''INSERT INTO inventory_history
                           (medicine_id, medicine_name, type, quantity,
                            price, total_amount, operator, notes)
                           VALUES (?, ?, ?, ?, ?, ?, ?, ?)''',
                        (item.medicine_id, item.medicine_name, '出库', item.quantity,
                         item.price, item.quantity * item.price,
                         prescription.created_by, f"处方#{prescription_id}")
                    )

                _log_operation(self.db, 'CREATE', 'prescription', prescription_id,
                               f"创建处方: 患者 {prescription.patient_name}")
        except Exception as e:
            raise ServiceError(f"创建处方失败: {e}")

        return prescription_id

    def get_by_id(self, prescription_id: int) -> Optional[Prescription]:
        row = self._repo.find_by_id(prescription_id)
        if not row:
            return None

        prescription = Prescription.from_dict(row)
        items_rows = self._repo.find_items(prescription_id)
        prescription.items = [PrescriptionItem.from_dict(item) for item in items_rows]
        return prescription

    def get_all(self, start_date: str = None, end_date: str = None,
                patient_name: str = None, limit: int = 100,
                load_items: bool = False, offset: int = None) -> List[Prescription]:
        rows = self._repo.find_all(start_date, end_date, patient_name, limit, offset=offset)
        prescriptions = [Prescription.from_dict(row) for row in rows]

        if load_items:
            for pres in prescriptions:
                items_rows = self._repo.find_items(pres.id)
                pres.items = [PrescriptionItem.from_dict(item) for item in items_rows]

        return prescriptions

    def count_all(self, start_date: str = None, end_date: str = None,
                  patient_name: str = None) -> int:
        """统计满足筛选条件的处方总数（用于分页）"""
        return self._repo.count_all(start_date, end_date, patient_name)

    def delete(self, prescription_id: int, operator: str = '') -> bool:
        prescription = self.get_by_id(prescription_id)
        if not prescription:
            raise ServiceError("处方不存在")

        try:
            with self.db.transaction():
                for item in prescription.items:
                    # 在主事务内通过 SQL 回退库存，避免跨 Service 事务隔离问题
                    inv_row = self.db.fetchone(
                        'SELECT quantity FROM inventory WHERE medicine_id = ?',
                        (item.medicine_id,)
                    )
                    if inv_row:
                        current_qty = inv_row['quantity'] if isinstance(inv_row, dict) else inv_row[0]
                        self.db.execute(
                            'UPDATE inventory SET quantity = ? WHERE medicine_id = ?',
                            (current_qty + item.quantity, item.medicine_id)
                        )
                        self.db.execute(
                            '''INSERT INTO inventory_history
                               (medicine_id, medicine_name, type, quantity,
                                price, total_amount, operator, notes)
                               VALUES (?, ?, ?, ?, ?, ?, ?, ?)''',
                            (item.medicine_id, item.medicine_name, '入库', item.quantity,
                             item.price, item.quantity * item.price,
                             operator, f"删除处方#{prescription_id}退货")
                        )

                self._repo.delete_items_by_prescription(prescription_id)
                self._repo.delete_by_id(prescription_id)

                _log_operation(self.db, 'DELETE', 'prescription', prescription_id,
                               f"删除处方: 患者 {prescription.patient_name}")
        except Exception as e:
            raise ServiceError(f"删除处方失败: {e}")

        return True

    def get_statistics(self, start_date: str = None, end_date: str = None) -> Dict[str, Any]:
        return self._repo.get_statistics(start_date, end_date)

    def get_items_by_id(self, prescription_id: int) -> List[Dict[str, Any]]:
        """查询处方明细列表（替代 history_view 直接查 prescription_items 表）"""
        return self._repo.find_items(prescription_id)

    def get_operation_logs(self, target_type: str = 'prescription', limit: int = 100) -> List[Dict[str, Any]]:
        """查询操作日志（替代 history_view 直接查 operation_logs 表）"""
        from core.repositories import OperationLogRepository
        return OperationLogRepository(self.db).find_by_target_type(target_type, limit)


class DataLoader:
    def __init__(self, db: Database = None):
        self.db = db or Database()
        from core.repositories import MedicineRepository
        self._repo = MedicineRepository(self.db)

    def load_builtin_data(self, data: List[Dict], force: bool = False) -> Tuple[int, int, List[str]]:
        added_count = 0
        updated_count = 0
        errors = []

        try:
            with self.db.transaction():
                for item in data:
                    try:
                        name = item.get('name', '').strip()
                        if not name:
                            errors.append("跳过无效数据: 缺少名称")
                            continue

                        existing_id = self._repo.find_id_by_name(name)

                        if existing_id and not force:
                            continue

                        if existing_id:
                            self._repo.update_with_inventory(existing_id, item)
                            updated_count += 1
                        else:
                            self._repo.insert_with_inventory(item)
                            added_count += 1

                    except Exception as e:
                        errors.append(f"处理 '{item.get('name', '未知')}' 时出错: {str(e)}")

                self._repo.record_data_version(len(data), self._calculate_checksum(len(data)))
        except Exception as e:
            raise ServiceError(f"加载数据失败: {e}")

        return added_count, updated_count, errors

    def _calculate_checksum(self, count: int) -> str:
        data_str = f"medicine_count:{count}"
        return hashlib.md5(data_str.encode()).hexdigest()

    def get_data_version(self) -> Optional[Dict]:
        return self._repo.find_latest_data_version()

    def verify_data_integrity(self, expected_count: int = None) -> Tuple[bool, List[str]]:
        errors = []

        actual_count = self._repo.count_medicines()
        if expected_count is not None and actual_count != expected_count:
            errors.append(f"药材数量不匹配: 期望 {expected_count}, 实际 {actual_count}")

        inv_check = self._repo.find_medicines_without_inventory()
        if inv_check:
            errors.append(f"以下药材缺少库存记录: {', '.join(row['name'] for row in inv_check)}")

        orphan_inv = self._repo.find_orphan_inventory()
        if orphan_inv:
            errors.append(f"发现 {len(orphan_inv)} 条孤立的库存记录")

        return len(errors) == 0, errors


class DashboardService:
    """仪表盘首页业务服务，封装 dashboard_view 所需聚合数据。"""

    def __init__(self, db: Database = None):
        self.db = db or Database()
        from core.repositories import StatisticsRepository
        self._stats_repo = StatisticsRepository(self.db)

    def get_today_summary(self) -> Dict[str, Any]:
        """今日处方数与营收"""
        now = datetime.now()
        today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        return self._stats_repo.find_today_summary(today_start, now)

    def get_medicine_count(self) -> int:
        """药材总数"""
        return self._stats_repo.count_medicines()

    def get_low_stock_alerts(self, limit: int = 10) -> List[Dict[str, Any]]:
        """低库存预警列表"""
        return self._stats_repo.find_low_stock_alerts(limit)

    def get_recent_prescriptions(self, limit: int = 5) -> List[Dict[str, Any]]:
        """最近处方列表"""
        return self._stats_repo.find_recent_prescriptions(limit)

    def get_revenue_trend_7_days(self) -> List[Dict[str, Any]]:
        """近 7 天营收趋势"""
        now = datetime.now()
        seven_days_ago = now - timedelta(days=6)
        start_str = seven_days_ago.replace(
            hour=0, minute=0, second=0, microsecond=0
        ).strftime('%Y-%m-%d %H:%M:%S')
        end_str = now.strftime('%Y-%m-%d %H:%M:%S')
        return self._stats_repo.find_revenue_trend_7_days(start_str, end_str)


class StatisticsService:
    """销售统计业务服务，封装 statistics_view 所需聚合数据。"""

    def __init__(self, db: Database = None):
        self.db = db or Database()
        from core.repositories import StatisticsRepository
        self._stats_repo = StatisticsRepository(self.db)

    def get_summary(self, start_date: str, end_date: str) -> Dict[str, Any]:
        """指定时间范围内的处方数与营收汇总"""
        return self._stats_repo.find_prescription_summary(start_date, end_date)

    def get_medicine_count(self) -> int:
        """药材总数"""
        return self._stats_repo.count_medicines()

    def get_low_stock_count(self) -> int:
        """低库存药材数量"""
        return self._stats_repo.count_low_stock()

    def get_top_medicines(self, start_date: str, end_date: str, limit: int = 10) -> List[Dict[str, Any]]:
        """热销药材 TOP N"""
        return self._stats_repo.find_top_medicines(start_date, end_date, limit)

    def get_revenue_trend(self, start_date: str, end_date: str, limit: int = 30) -> List[Dict[str, Any]]:
        """营收趋势"""
        return self._stats_repo.find_revenue_trend(start_date, end_date, limit)


class PatientService:
    """患者档案业务服务，封装 PatientView 所需的档案管理与历史处方查询。"""

    def __init__(self, db: Database = None):
        self.db = db or Database()
        from core.repositories import PatientRepository
        self._repo = PatientRepository(self.db)

    def create(self, patient: Patient) -> int:
        """创建患者档案。

        允许同名患者（不同人可能同名），不做唯一性校验。
        """
        errors = patient.validate_fields()
        if errors:
            raise ServiceError(f"数据验证失败: {', '.join(errors)}")

        try:
            with self.db.transaction():
                patient_id = self._repo.insert_patient(patient)
                _log_operation(self.db, 'CREATE', 'patient', patient_id,
                               f"创建患者档案: {patient.name}")
        except Exception as e:
            raise ServiceError(f"创建患者档案失败: {e}")

        return patient_id

    def update(self, patient: Patient) -> bool:
        if not patient.id:
            raise ServiceError("患者ID不能为空")

        errors = patient.validate_fields()
        if errors:
            raise ServiceError(f"数据验证失败: {', '.join(errors)}")

        existing = self.get_by_id(patient.id)
        if not existing:
            raise ServiceError("患者档案不存在")

        try:
            with self.db.transaction():
                self._repo.update_patient(patient)
                _log_operation(self.db, 'UPDATE', 'patient', patient.id,
                               f"更新患者档案: {patient.name}")
        except Exception as e:
            raise ServiceError(f"更新患者档案失败: {e}")

        return True

    def delete(self, patient_id: int) -> bool:
        patient = self.get_by_id(patient_id)
        if not patient:
            raise ServiceError("患者档案不存在")

        try:
            with self.db.transaction():
                self._repo.delete_by_id(patient_id)
                _log_operation(self.db, 'DELETE', 'patient', patient_id,
                               f"删除患者档案: {patient.name}")
        except Exception as e:
            raise ServiceError(f"删除患者档案失败: {e}")

        return True

    def get_by_id(self, patient_id: int) -> Optional[Patient]:
        row = self._repo.find_by_id(patient_id)
        return Patient.from_dict(row) if row else None

    def search(self, keyword: str = "") -> List[Patient]:
        """按姓名/电话搜索患者"""
        rows = self._repo.find_all(keyword=keyword)
        return [Patient.from_dict(row) for row in rows]

    def get_by_name(self, name: str) -> Optional[Patient]:
        """按姓名精确查询（返回首条匹配，调用方需自行处理同名场景）"""
        row = self._repo.find_by_name(name)
        return Patient.from_dict(row) if row else None

    def get_prescriptions(self, patient_id: int) -> List[Dict[str, Any]]:
        """获取患者处方历史（通过 patient.name 关联 prescriptions.patient_name）"""
        patient = self.get_by_id(patient_id)
        if not patient:
            return []
        return self._repo.find_prescriptions_by_name(patient.name)

    def get_statistics(self, patient_id: int) -> Dict[str, Any]:
        """获取患者统计数据（处方数、总消费、首次就诊、最近就诊）"""
        patient = self.get_by_id(patient_id)
        if not patient:
            return {
                'prescription_count': 0,
                'total_amount': 0.0,
                'first_visit': None,
                'last_visit': None,
            }
        return self._repo.find_statistics_by_name(patient.name)
