# -*- coding: utf-8 -*-
"""
服务层 - 业务逻辑处理
"""
from typing import Optional, List, Dict, Any, Tuple
from datetime import datetime
import hashlib

from .database import Database, DatabaseError
from .models import Medicine, Inventory, Prescription, PrescriptionItem, InventoryHistory, OperationLog


class ServiceError(Exception):
    pass


class MedicineService:
    def __init__(self, db: Database = None):
        self.db = db or Database()
    
    def get_all(self, category: str = None, keyword: str = None) -> List[Medicine]:
        query = '''
            SELECT m.*, i.quantity, i.unit, i.price, i.min_stock 
            FROM medicines m 
            LEFT JOIN inventory i ON m.id = i.medicine_id
            WHERE 1=1
        '''
        params = []
        
        if category:
            query += ' AND m.category = ?'
            params.append(category)
        
        if keyword:
            query += ' AND (m.name LIKE ? OR m.alias LIKE ? OR m.efficacy LIKE ?)'
            keyword_param = f'%{keyword}%'
            params.extend([keyword_param, keyword_param, keyword_param])
        
        query += ' ORDER BY m.name'
        
        rows = self.db.fetchall(query, tuple(params))
        return [Medicine.from_dict(row) for row in rows]
    
    def get_by_id(self, medicine_id: int) -> Optional[Medicine]:
        query = '''
            SELECT m.*, i.quantity, i.unit, i.price, i.min_stock 
            FROM medicines m 
            LEFT JOIN inventory i ON m.id = i.medicine_id
            WHERE m.id = ?
        '''
        row = self.db.fetchone(query, (medicine_id,))
        return Medicine.from_dict(row) if row else None
    
    def get_by_name(self, name: str) -> Optional[Medicine]:
        query = '''
            SELECT m.*, i.quantity, i.unit, i.price, i.min_stock 
            FROM medicines m 
            LEFT JOIN inventory i ON m.id = i.medicine_id
            WHERE m.name = ?
        '''
        row = self.db.fetchone(query, (name,))
        return Medicine.from_dict(row) if row else None
    
    def create(self, medicine: Medicine) -> int:
        errors = medicine.validate()
        if errors:
            raise ServiceError(f"数据验证失败: {', '.join(errors)}")
        
        existing = self.get_by_name(medicine.name)
        if existing:
            raise ServiceError(f"药材 '{medicine.name}' 已存在")
        
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
        
        cursor = self.db.execute(query, params)
        medicine_id = cursor.lastrowid
        
        inv_query = '''
            INSERT INTO inventory (medicine_id, quantity, unit, price, min_stock, notes)
            VALUES (?, 0, 'g', 0, 0, '')
        '''
        self.db.execute(inv_query, (medicine_id,))
        
        self._log_operation('CREATE', 'medicine', medicine_id, f"创建药材: {medicine.name}")
        
        return medicine_id
    
    def update(self, medicine: Medicine) -> bool:
        if not medicine.id:
            raise ServiceError("药材ID不能为空")
        
        errors = medicine.validate()
        if errors:
            raise ServiceError(f"数据验证失败: {', '.join(errors)}")
        
        existing = self.get_by_name(medicine.name)
        if existing and existing.id != medicine.id:
            raise ServiceError(f"药材名称 '{medicine.name}' 已被其他药材使用")
        
        query = '''
            UPDATE medicines SET name=?, alias=?, category=?, nature=?, taste=?, 
                                  meridian=?, efficacy=?, indications=?, usage=?, 
                                  dosage=?, contraindication=?, notes=?, updated_at=CURRENT_TIMESTAMP
            WHERE id=?
        '''
        params = (
            medicine.name, medicine.alias, medicine.category, medicine.nature,
            medicine.taste, medicine.meridian, medicine.efficacy, medicine.indications,
            medicine.usage, medicine.dosage, medicine.contraindication, medicine.notes,
            medicine.id
        )
        
        self.db.execute(query, params)
        self._log_operation('UPDATE', 'medicine', medicine.id, f"更新药材: {medicine.name}")
        
        return True
    
    def delete(self, medicine_id: int) -> bool:
        medicine = self.get_by_id(medicine_id)
        if not medicine:
            raise ServiceError("药材不存在")
        
        query = 'DELETE FROM medicines WHERE id = ?'
        self.db.execute(query, (medicine_id,))
        
        self._log_operation('DELETE', 'medicine', medicine_id, f"删除药材: {medicine.name}")
        
        return True
    
    def get_categories(self) -> List[str]:
        query = 'SELECT DISTINCT category FROM medicines WHERE category IS NOT NULL ORDER BY category'
        rows = self.db.fetchall(query)
        return [row['category'] for row in rows]
    
    def search(self, keyword: str, fields: List[str] = None) -> List[Medicine]:
        if not keyword:
            return []
        
        if fields is None:
            fields = ['name', 'alias', 'efficacy', 'indications']
        
        conditions = []
        params = []
        for field in fields:
            if field in ['name', 'alias', 'efficacy', 'indications', 'category', 'nature', 'taste']:
                conditions.append(f'm.{field} LIKE ?')
                params.append(f'%{keyword}%')
        
        if not conditions:
            return []
        
        query = f'''
            SELECT m.*, i.quantity, i.unit, i.price, i.min_stock 
            FROM medicines m 
            LEFT JOIN inventory i ON m.id = i.medicine_id
            WHERE {' OR '.join(conditions)}
            ORDER BY m.name
        '''
        
        rows = self.db.fetchall(query, tuple(params))
        return [Medicine.from_dict(row) for row in rows]
    
    def _log_operation(self, operation_type: str, target_type: str, target_id: int, details: str = ''):
        query = '''
            INSERT INTO operation_logs (operation_type, target_type, target_id, details)
            VALUES (?, ?, ?, ?)
        '''
        self.db.execute(query, (operation_type, target_type, target_id, details))


class InventoryService:
    def __init__(self, db: Database = None):
        self.db = db or Database()
    
    def get_all(self, low_stock_only: bool = False) -> List[Inventory]:
        query = '''
            SELECT i.*, m.name as medicine_name 
            FROM inventory i 
            JOIN medicines m ON i.medicine_id = m.id
        '''
        
        if low_stock_only:
            query += ' WHERE i.quantity <= i.min_stock'
        
        query += ' ORDER BY m.name'
        
        rows = self.db.fetchall(query)
        return [Inventory.from_dict(row) for row in rows]
    
    def get_by_medicine_id(self, medicine_id: int) -> Optional[Inventory]:
        query = '''
            SELECT i.*, m.name as medicine_name 
            FROM inventory i 
            JOIN medicines m ON i.medicine_id = m.id
            WHERE i.medicine_id = ?
        '''
        row = self.db.fetchone(query, (medicine_id,))
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
        
        update_query = '''
            UPDATE inventory SET quantity = ?, updated_at = CURRENT_TIMESTAMP 
            WHERE medicine_id = ?
        '''
        self.db.execute(update_query, (new_quantity, medicine_id))
        
        if price is not None:
            price_query = 'UPDATE inventory SET price = ? WHERE medicine_id = ?'
            self.db.execute(price_query, (price, medicine_id))
        
        total_amount = None
        if price is not None and quantity_change != 0:
            total_amount = abs(quantity_change) * price
        
        history_query = '''
            INSERT INTO inventory_history (medicine_id, medicine_name, type, quantity, price, total_amount, operator, notes)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        '''
        self.db.execute(history_query, (
            medicine_id, inventory.medicine_name, operation_type, 
            abs(quantity_change), price, total_amount, operator, notes
        ))
        
        return True
    
    def stock_in(self, medicine_id: int, quantity: float, price: float = None, 
                 notes: str = '', operator: str = '') -> bool:
        return self.update_stock(medicine_id, quantity, '入库', price, notes, operator)
    
    def stock_out(self, medicine_id: int, quantity: float, price: float = None, 
                  notes: str = '', operator: str = '') -> bool:
        return self.update_stock(medicine_id, -quantity, '出库', price, notes, operator)
    
    def get_history(self, medicine_id: int = None, limit: int = 100) -> List[InventoryHistory]:
        query = 'SELECT * FROM inventory_history'
        params = []
        
        if medicine_id:
            query += ' WHERE medicine_id = ?'
            params.append(medicine_id)
        
        query += ' ORDER BY created_at DESC LIMIT ?'
        params.append(limit)
        
        rows = self.db.fetchall(query, tuple(params))
        return [InventoryHistory.from_dict(row) for row in rows]
    
    def get_low_stock_items(self) -> List[Inventory]:
        return self.get_all(low_stock_only=True)
    
    def update_price(self, medicine_id: int, price: float) -> bool:
        query = 'UPDATE inventory SET price = ?, updated_at = CURRENT_TIMESTAMP WHERE medicine_id = ?'
        self.db.execute(query, (price, medicine_id))
        return True
    
    def update_min_stock(self, medicine_id: int, min_stock: float) -> bool:
        query = 'UPDATE inventory SET min_stock = ?, updated_at = CURRENT_TIMESTAMP WHERE medicine_id = ?'
        self.db.execute(query, (min_stock, medicine_id))
        return True


class PrescriptionService:
    def __init__(self, db: Database = None):
        self.db = db or Database()
        self.medicine_service = MedicineService(db)
        self.inventory_service = InventoryService(db)
    
    def create(self, prescription: Prescription, items: List[PrescriptionItem]) -> int:
        self.db.begin_transaction()
        
        try:
            pres_query = '''
                INSERT INTO prescriptions (patient_name, patient_age, patient_gender, diagnosis, total_amount, created_by)
                VALUES (?, ?, ?, ?, ?, ?)
            '''
            cursor = self.db.execute(pres_query, (
                prescription.patient_name, prescription.patient_age,
                prescription.patient_gender, prescription.diagnosis,
                prescription.total_amount, prescription.created_by
            ))
            prescription_id = cursor.lastrowid
            
            for item in items:
                item_query = '''
                    INSERT INTO prescription_items (prescription_id, medicine_id, medicine_name, quantity, unit, price, amount)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                '''
                self.db.execute(item_query, (
                    prescription_id, item.medicine_id, item.medicine_name,
                    item.quantity, item.unit, item.price, item.amount
                ))
                
                self.inventory_service.stock_out(
                    item.medicine_id, item.quantity, item.price,
                    f"处方#{prescription_id}", prescription.created_by
                )
            
            self.db.commit()
            
            self._log_operation('CREATE', 'prescription', prescription_id, 
                               f"创建处方: 患者 {prescription.patient_name}")
            
            return prescription_id
            
        except Exception as e:
            self.db.rollback()
            raise ServiceError(f"创建处方失败: {e}")
    
    def get_by_id(self, prescription_id: int) -> Optional[Prescription]:
        query = 'SELECT * FROM prescriptions WHERE id = ?'
        row = self.db.fetchone(query, (prescription_id,))
        
        if not row:
            return None
        
        prescription = Prescription.from_dict(row)
        
        items_query = 'SELECT * FROM prescription_items WHERE prescription_id = ?'
        items_rows = self.db.fetchall(items_query, (prescription_id,))
        prescription.items = [PrescriptionItem.from_dict(item) for item in items_rows]
        
        return prescription
    
    def get_all(self, start_date: str = None, end_date: str = None, 
                patient_name: str = None, limit: int = 100) -> List[Prescription]:
        query = 'SELECT * FROM prescriptions WHERE 1=1'
        params = []
        
        if start_date:
            query += ' AND DATE(created_at) >= ?'
            params.append(start_date)
        
        if end_date:
            query += ' AND DATE(created_at) <= ?'
            params.append(end_date)
        
        if patient_name:
            query += ' AND patient_name LIKE ?'
            params.append(f'%{patient_name}%')
        
        query += ' ORDER BY created_at DESC LIMIT ?'
        params.append(limit)
        
        rows = self.db.fetchall(query, tuple(params))
        return [Prescription.from_dict(row) for row in rows]
    
    def delete(self, prescription_id: int, operator: str = '') -> bool:
        prescription = self.get_by_id(prescription_id)
        if not prescription:
            raise ServiceError("处方不存在")
        
        self.db.begin_transaction()
        
        try:
            for item in prescription.items:
                self.inventory_service.stock_in(
                    item.medicine_id, item.quantity, item.price,
                    f"删除处方#{prescription_id}退货", operator
                )
            
            items_query = 'DELETE FROM prescription_items WHERE prescription_id = ?'
            self.db.execute(items_query, (prescription_id,))
            
            pres_query = 'DELETE FROM prescriptions WHERE id = ?'
            self.db.execute(pres_query, (prescription_id,))
            
            self.db.commit()
            
            self._log_operation('DELETE', 'prescription', prescription_id,
                               f"删除处方: 患者 {prescription.patient_name}")
            
            return True
            
        except Exception as e:
            self.db.rollback()
            raise ServiceError(f"删除处方失败: {e}")
    
    def get_statistics(self, start_date: str = None, end_date: str = None) -> Dict[str, Any]:
        query = '''
            SELECT COUNT(*) as count, COALESCE(SUM(total_amount), 0) as total_amount
            FROM prescriptions WHERE 1=1
        '''
        params = []
        
        if start_date:
            query += ' AND DATE(created_at) >= ?'
            params.append(start_date)
        
        if end_date:
            query += ' AND DATE(created_at) <= ?'
            params.append(end_date)
        
        row = self.db.fetchone(query, tuple(params))
        
        return {
            'prescription_count': row['count'] if row else 0,
            'total_amount': row['total_amount'] if row else 0
        }
    
    def _log_operation(self, operation_type: str, target_type: str, target_id: int, details: str = ''):
        query = '''
            INSERT INTO operation_logs (operation_type, target_type, target_id, details)
            VALUES (?, ?, ?, ?)
        '''
        self.db.execute(query, (operation_type, target_type, target_id, details))


class DataLoader:
    def __init__(self, db: Database = None):
        self.db = db or Database()
    
    def load_builtin_data(self, data: List[Dict], force: bool = False) -> Tuple[int, int, List[str]]:
        added_count = 0
        updated_count = 0
        errors = []
        
        self.db.begin_transaction()
        
        try:
            for item in data:
                try:
                    name = item.get('name', '').strip()
                    if not name:
                        errors.append(f"跳过无效数据: 缺少名称")
                        continue
                    
                    existing = self.db.fetchone(
                        'SELECT id FROM medicines WHERE name = ?', (name,)
                    )
                    
                    if existing and not force:
                        continue
                    
                    if existing:
                        self._update_medicine(existing['id'], item)
                        updated_count += 1
                    else:
                        self._insert_medicine(item)
                        added_count += 1
                        
                except Exception as e:
                    errors.append(f"处理 '{item.get('name', '未知')}' 时出错: {str(e)}")
            
            self._update_data_version(len(data))
            
            self.db.commit()
            
        except Exception as e:
            self.db.rollback()
            raise ServiceError(f"加载数据失败: {e}")
        
        return added_count, updated_count, errors
    
    def _insert_medicine(self, item: Dict):
        med_query = '''
            INSERT INTO medicines (name, alias, category, nature, taste, meridian, 
                                   efficacy, indications, usage, dosage, contraindication, notes)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        '''
        cursor = self.db.execute(med_query, (
            item.get('name', ''),
            item.get('alias', ''),
            item.get('category', ''),
            item.get('nature', ''),
            item.get('taste', ''),
            item.get('meridian', ''),
            item.get('efficacy', ''),
            item.get('indications', ''),
            item.get('usage', ''),
            item.get('dosage', ''),
            item.get('contraindication', ''),
            item.get('notes', '')
        ))
        
        medicine_id = cursor.lastrowid
        
        inv_query = '''
            INSERT INTO inventory (medicine_id, quantity, unit, price, min_stock, notes)
            VALUES (?, ?, ?, ?, ?, ?)
        '''
        self.db.execute(inv_query, (
            medicine_id,
            item.get('quantity', 0),
            item.get('unit', 'g'),
            item.get('price', 0),
            item.get('min_stock', 0),
            item.get('notes', '')
        ))
    
    def _update_medicine(self, medicine_id: int, item: Dict):
        med_query = '''
            UPDATE medicines SET alias=?, category=?, nature=?, taste=?, meridian=?, 
                                  efficacy=?, indications=?, usage=?, dosage=?, 
                                  contraindication=?, notes=?, updated_at=CURRENT_TIMESTAMP
            WHERE id=?
        '''
        self.db.execute(med_query, (
            item.get('alias', ''),
            item.get('category', ''),
            item.get('nature', ''),
            item.get('taste', ''),
            item.get('meridian', ''),
            item.get('efficacy', ''),
            item.get('indications', ''),
            item.get('usage', ''),
            item.get('dosage', ''),
            item.get('contraindication', ''),
            item.get('notes', ''),
            medicine_id
        ))
        
        inv_query = '''
            UPDATE inventory SET quantity=?, unit=?, price=?, min_stock=?, updated_at=CURRENT_TIMESTAMP
            WHERE medicine_id=?
        '''
        self.db.execute(inv_query, (
            item.get('quantity', 0),
            item.get('unit', 'g'),
            item.get('price', 0),
            item.get('min_stock', 0),
            medicine_id
        ))
    
    def _update_data_version(self, medicine_count: int):
        checksum = self._calculate_checksum(medicine_count)
        
        query = '''
            INSERT INTO data_version (version, medicine_count, checksum)
            VALUES (?, ?, ?)
        '''
        from datetime import datetime
        version = datetime.now().strftime('%Y%m%d%H%M%S')
        self.db.execute(query, (version, medicine_count, checksum))
    
    def _calculate_checksum(self, count: int) -> str:
        data_str = f"medicine_count:{count}"
        return hashlib.md5(data_str.encode()).hexdigest()
    
    def get_data_version(self) -> Optional[Dict]:
        query = 'SELECT * FROM data_version ORDER BY created_at DESC LIMIT 1'
        return self.db.fetchone(query)
    
    def verify_data_integrity(self, expected_count: int = None) -> Tuple[bool, List[str]]:
        errors = []
        
        med_count = self.db.fetchone('SELECT COUNT(*) as count FROM medicines')
        actual_count = med_count['count'] if med_count else 0
        
        if expected_count is not None and actual_count != expected_count:
            errors.append(f"药材数量不匹配: 期望 {expected_count}, 实际 {actual_count}")
        
        inv_check = self.db.fetchall('''
            SELECT m.name FROM medicines m 
            LEFT JOIN inventory i ON m.id = i.medicine_id 
            WHERE i.id IS NULL
        ''')
        if inv_check:
            errors.append(f"以下药材缺少库存记录: {', '.join(row['name'] for row in inv_check)}")
        
        orphan_inv = self.db.fetchall('''
            SELECT i.medicine_id FROM inventory i 
            LEFT JOIN medicines m ON i.medicine_id = m.id 
            WHERE m.id IS NULL
        ''')
        if orphan_inv:
            errors.append(f"发现 {len(orphan_inv)} 条孤立的库存记录")
        
        return len(errors) == 0, errors
