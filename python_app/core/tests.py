# -*- coding: utf-8 -*-
"""
单元测试模块 - 测试核心功能
"""
import unittest
import os
import sys
import tempfile
import shutil
from typing import List, Dict, Any

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.database import Database, DatabaseError
from core.models import Medicine, Inventory, Prescription, PrescriptionItem
from core.services import MedicineService, InventoryService, PrescriptionService, DataLoader
from core.cache import MedicineCache, LRUCache
from core.validators import MedicineValidator, PrescriptionValidator
from core.exceptions import AppException, ValidationException, ServiceException, Result


class TestDatabase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp_dir = tempfile.mkdtemp()
        cls.db_path = os.path.join(cls.temp_dir, 'test.db')
    
    @classmethod
    def tearDownClass(cls):
        if os.path.exists(cls.temp_dir):
            shutil.rmtree(cls.temp_dir)
    
    def setUp(self):
        Database.reset_instance()
        self.db = Database(self.db_path)
    
    def tearDown(self):
        self.db.close()
        Database.reset_instance()
    
    def test_connection(self):
        self.assertIsNotNone(self.db.conn)
        self.assertIsNotNone(self.db.cursor)
    
    def test_tables_created(self):
        tables = self.db.fetchall(
            "SELECT name FROM sqlite_master WHERE type='table'"
        )
        table_names = [t['name'] for t in tables]
        self.assertIn('medicines', table_names)
        self.assertIn('inventory', table_names)
        self.assertIn('prescriptions', table_names)
    
    def test_insert_and_query(self):
        self.db.execute(
            "INSERT INTO medicines (name, category, nature, taste, meridian, efficacy, indications) VALUES (?, ?, ?, ?, ?, ?, ?)",
            ('测试药材', '测试分类', '温', '甘', '归脾经', '测试功效', '测试主治')
        )
        
        result = self.db.fetchone("SELECT * FROM medicines WHERE name = ?", ('测试药材',))
        self.assertIsNotNone(result)
        self.assertEqual(result['name'], '测试药材')
    
    def test_transaction_rollback(self):
        self.db.cursor.execute("BEGIN")
        self.db.cursor.execute(
            "INSERT INTO medicines (name, category, nature, taste, meridian, efficacy, indications) VALUES (?, ?, ?, ?, ?, ?, ?)",
            ('事务测试药材', '测试', '温', '甘', '归脾经', '功效', '主治')
        )
        self.db.conn.rollback()
        
        result = self.db.fetchone("SELECT * FROM medicines WHERE name = ?", ('事务测试药材',))
        self.assertIsNone(result)


class TestModels(unittest.TestCase):
    def test_medicine_creation(self):
        medicine = Medicine(
            name='人参',
            category='补虚药',
            nature='温',
            taste='甘、微苦',
            meridian='归脾、肺、心经',
            efficacy='大补元气',
            indications='体虚欲脱'
        )
        
        self.assertEqual(medicine.name, '人参')
        self.assertEqual(medicine.category, '补虚药')
    
    def test_medicine_validation(self):
        medicine = Medicine(name='')
        errors = medicine.validate()
        self.assertIn('药材名称不能为空', errors)
        
        medicine2 = Medicine(
            name='测试',
            category='分类',
            nature='温',
            taste='甘',
            meridian='归经',
            efficacy='功效',
            indications='主治'
        )
        errors2 = medicine2.validate()
        self.assertEqual(len(errors2), 0)
    
    def test_medicine_to_dict(self):
        medicine = Medicine(
            id=1,
            name='测试',
            category='分类'
        )
        data = medicine.to_dict()
        self.assertEqual(data['id'], 1)
        self.assertEqual(data['name'], '测试')
    
    def test_inventory_low_stock(self):
        inventory = Inventory(
            medicine_id=1,
            quantity=5,
            min_stock=10
        )
        self.assertTrue(inventory.is_low_stock())
        
        inventory2 = Inventory(
            medicine_id=2,
            quantity=20,
            min_stock=10
        )
        self.assertFalse(inventory2.is_low_stock())


class TestCache(unittest.TestCase):
    def test_lru_cache_basic(self):
        cache = LRUCache(max_size=3)
        
        cache.set('a', 1)
        cache.set('b', 2)
        cache.set('c', 3)
        
        self.assertEqual(cache.get('a'), 1)
        self.assertEqual(cache.get('b'), 2)
        self.assertEqual(cache.get('c'), 3)
    
    def test_lru_cache_eviction(self):
        cache = LRUCache(max_size=2)
        
        cache.set('a', 1)
        cache.set('b', 2)
        cache.set('c', 3)
        
        self.assertIsNone(cache.get('a'))
        self.assertEqual(cache.get('b'), 2)
        self.assertEqual(cache.get('c'), 3)
    
    def test_lru_cache_ttl(self):
        cache = LRUCache(max_size=10, default_ttl=0.1)
        
        cache.set('a', 1)
        self.assertEqual(cache.get('a'), 1)
        
        import time
        time.sleep(0.15)
        
        self.assertIsNone(cache.get('a'))
    
    def test_medicine_cache(self):
        cache = MedicineCache()
        
        medicines = [
            {'id': 1, 'name': '人参', 'category': '补虚药', 'nature': '温'},
            {'id': 2, 'name': '黄芪', 'category': '补虚药', 'nature': '微温'},
            {'id': 3, 'name': '当归', 'category': '补虚药', 'nature': '温'},
        ]
        
        cache.initialize(medicines)
        
        self.assertEqual(cache.get_by_id(1)['name'], '人参')
        self.assertEqual(cache.get_by_name('人参')['id'], 1)
        self.assertEqual(len(cache.get_by_category('补虚药')), 3)
    
    def test_medicine_cache_search(self):
        cache = MedicineCache()
        
        medicines = [
            {'id': 1, 'name': '人参', 'category': '补虚药', 'nature': '温', 'efficacy': '大补元气'},
            {'id': 2, 'name': '黄芪', 'category': '补虚药', 'nature': '微温', 'efficacy': '补气升阳'},
            {'id': 3, 'name': '当归', 'category': '补虚药', 'nature': '温', 'efficacy': '补血活血'},
        ]
        
        cache.initialize(medicines)
        
        results = cache.search('人')
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]['name'], '人参')
        
        results2 = cache.search('', category='补虚药', nature='温')
        self.assertEqual(len(results2), 2)


class TestValidators(unittest.TestCase):
    def test_medicine_validator(self):
        valid_data = {
            'name': '人参',
            'category': '补虚药',
            'nature': '温',
            'taste': '甘',
            'meridian': '归脾经',
            'efficacy': '补气',
            'indications': '气虚'
        }
        
        is_valid, errors = MedicineValidator.validate(valid_data)
        self.assertTrue(is_valid)
        self.assertEqual(len(errors), 0)
    
    def test_medicine_validator_missing_name(self):
        invalid_data = {
            'category': '补虚药',
            'nature': '温'
        }
        
        is_valid, errors = MedicineValidator.validate(invalid_data)
        self.assertFalse(is_valid)
        self.assertIn('药材名称不能为空', errors)
    
    def test_medicine_validator_negative_quantity(self):
        data = {
            'name': '测试',
            'category': '分类',
            'nature': '温',
            'taste': '甘',
            'meridian': '归经',
            'efficacy': '功效',
            'indications': '主治',
            'quantity': -10
        }
        
        is_valid, errors = MedicineValidator.validate(data)
        self.assertFalse(is_valid)
        self.assertIn('库存数量不能为负数', errors)
    
    def test_prescription_validator(self):
        valid_data = {
            'patient_name': '张三',
            'patient_age': 30,
            'items': [
                {'medicine_name': '人参', 'quantity': 10, 'price': 50}
            ]
        }
        
        is_valid, errors = PrescriptionValidator.validate(valid_data)
        self.assertTrue(is_valid)
    
    def test_prescription_validator_empty_items(self):
        invalid_data = {
            'patient_name': '张三',
            'items': []
        }
        
        is_valid, errors = PrescriptionValidator.validate(invalid_data)
        self.assertFalse(is_valid)
        self.assertIn('处方必须包含至少一个药材', errors)


class TestExceptions(unittest.TestCase):
    def test_app_exception(self):
        exc = AppException("测试错误")
        self.assertEqual(str(exc), "[UNKNOWN_ERROR] 测试错误")
        
        data = exc.to_dict()
        self.assertFalse(data['success'])
        self.assertEqual(data['error']['message'], '测试错误')
    
    def test_validation_exception(self):
        exc = ValidationException(
            message="验证失败",
            field="name",
            errors=["名称不能为空"]
        )
        
        self.assertEqual(exc.details['field'], 'name')
        self.assertIn('名称不能为空', exc.details['errors'])
    
    def test_result_success(self):
        result = Result.ok(data={'id': 1}, message="成功")
        self.assertTrue(result.is_success)
        self.assertEqual(result.data['id'], 1)
    
    def test_result_failure(self):
        result = Result.fail(AppException("失败"))
        self.assertTrue(result.is_failure)
        self.assertIsNotNone(result.error)


def run_tests():
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    suite.addTests(loader.loadTestsFromTestCase(TestDatabase))
    suite.addTests(loader.loadTestsFromTestCase(TestModels))
    suite.addTests(loader.loadTestsFromTestCase(TestCache))
    suite.addTests(loader.loadTestsFromTestCase(TestValidators))
    suite.addTests(loader.loadTestsFromTestCase(TestExceptions))
    
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    return result.wasSuccessful()


if __name__ == '__main__':
    success = run_tests()
    sys.exit(0 if success else 1)
