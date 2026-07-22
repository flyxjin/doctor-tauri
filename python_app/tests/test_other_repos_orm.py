# -*- coding: utf-8 -*-
"""
InventoryRepository / PrescriptionRepository / OperationLogRepository
ORM 切换后的回归测试

验证阶段 2.3：只读方法走 SQLAlchemy ORM 后，行为与原 SQL 路径一致。
"""
from core.models import Medicine, Prescription, PrescriptionItem
from core.repositories import (
    InventoryRepository,
    OperationLogRepository,
    PrescriptionRepository,
)
from core.services import InventoryService, MedicineService, PrescriptionService


def _make_med(name, **kw):
    defaults = dict(
        name=name, category='补虚药', nature='温', taste='甘',
        meridian='归脾经', efficacy='补气', indications='体虚',
    )
    defaults.update(kw)
    return Medicine(**defaults)


class TestInventoryRepoORM:
    def test_find_all_returns_joined_fields(self, temp_db):
        svc = MedicineService(temp_db)
        med_id = svc.create(_make_med('人参'))
        inv_svc = InventoryService(temp_db)
        inv_svc.stock_in(med_id, 100, price=10.0)

        repo = InventoryRepository(temp_db)
        rows = repo.find_all()
        assert len(rows) == 1
        assert rows[0]['medicine_name'] == '人参'
        assert rows[0]['quantity'] == 100
        assert rows[0]['price'] == 10.0

    def test_find_all_low_stock_only(self, temp_db):
        svc = MedicineService(temp_db)
        med_id = svc.create(_make_med('低库存药材'))
        inv_svc = InventoryService(temp_db)
        inv_svc.stock_in(med_id, 5, price=10.0)
        # 直接更新 min_stock
        temp_db.execute('UPDATE inventory SET min_stock = 10 WHERE medicine_id = ?', (med_id,))

        repo = InventoryRepository(temp_db)
        low = repo.find_all(low_stock_only=True)
        assert any(r['medicine_id'] == med_id for r in low)

    def test_find_all_stock_status_filters(self, temp_db):
        svc = MedicineService(temp_db)
        med1 = svc.create(_make_med('充足药材'))
        med2 = svc.create(_make_med('缺货药材'))
        med3 = svc.create(_make_med('低库存药材'))

        inv_svc = InventoryService(temp_db)
        inv_svc.stock_in(med1, 100, price=1.0)
        # med2 不入库，quantity=0
        inv_svc.stock_in(med3, 3, price=1.0)
        temp_db.execute('UPDATE inventory SET min_stock = 10 WHERE medicine_id = ?', (med3,))

        repo = InventoryRepository(temp_db)
        # 缺货
        out = repo.find_all(stock_status='缺货')
        assert any(r['medicine_id'] == med2 for r in out)
        # 低库存
        low = repo.find_all(stock_status='低库存')
        assert any(r['medicine_id'] == med3 for r in low)
        # 充足
        ok = repo.find_all(stock_status='库存充足')
        assert any(r['medicine_id'] == med1 for r in ok)

    def test_find_by_medicine_id_missing(self, temp_db):
        repo = InventoryRepository(temp_db)
        assert repo.find_by_medicine_id(99999) is None

    def test_find_by_medicine_id_returns_medicine_name(self, temp_db):
        svc = MedicineService(temp_db)
        med_id = svc.create(_make_med('黄芪'))
        inv_svc = InventoryService(temp_db)
        inv_svc.stock_in(med_id, 50)

        repo = InventoryRepository(temp_db)
        row = repo.find_by_medicine_id(med_id)
        assert row is not None
        assert row['medicine_name'] == '黄芪'
        assert row['quantity'] == 50

    def test_find_history(self, temp_db):
        svc = MedicineService(temp_db)
        med_id = svc.create(_make_med('历史药材'))
        inv_svc = InventoryService(temp_db)
        inv_svc.stock_in(med_id, 100, price=10.0)
        inv_svc.stock_out(med_id, 30)

        repo = InventoryRepository(temp_db)
        history = repo.find_history(med_id)
        assert len(history) == 2
        # 倒序：最新在前
        types = [h['type'] for h in history]
        assert '出库' in types
        assert '入库' in types

    def test_find_history_all_medicines(self, temp_db):
        svc = MedicineService(temp_db)
        med1 = svc.create(_make_med('A'))
        med2 = svc.create(_make_med('B'))
        inv_svc = InventoryService(temp_db)
        inv_svc.stock_in(med1, 10)
        inv_svc.stock_in(med2, 20)

        repo = InventoryRepository(temp_db)
        all_history = repo.find_history()
        assert len(all_history) == 2


class TestPrescriptionRepoORM:
    def _make_prescription_with_item(self, med_id, qty=10, price=5.0):
        pres = Prescription(
            patient_name='测试患者', diagnosis='测试诊断', created_by='医生',
            total_amount=qty * price,
        )
        item = PrescriptionItem(
            prescription_id=0, medicine_id=med_id, medicine_name='测试药材',
            quantity=qty, unit='g', price=price, amount=qty * price,
        )
        return pres, [item]

    def test_find_by_id_missing(self, temp_db):
        repo = PrescriptionRepository(temp_db)
        assert repo.find_by_id(99999) is None

    def test_find_all_empty(self, temp_db):
        repo = PrescriptionRepository(temp_db)
        assert repo.find_all() == []

    def test_create_then_find(self, temp_db):
        med_svc = MedicineService(temp_db)
        med_id = med_svc.create(_make_med('人参'))

        inv_svc = InventoryService(temp_db)
        inv_svc.stock_in(med_id, 100, price=10.0)

        pres_svc = PrescriptionService(temp_db)
        pres, items = self._make_prescription_with_item(med_id, qty=10, price=10.0)
        pres_id = pres_svc.create(pres, items)

        repo = PrescriptionRepository(temp_db)
        found = repo.find_by_id(pres_id)
        assert found is not None
        assert found['patient_name'] == '测试患者'

        items_rows = repo.find_items(pres_id)
        assert len(items_rows) == 1
        assert items_rows[0]['medicine_name'] == '测试药材'

    def test_find_all_with_filters(self, temp_db):
        med_svc = MedicineService(temp_db)
        med_id = med_svc.create(_make_med('人参'))
        inv_svc = InventoryService(temp_db)
        inv_svc.stock_in(med_id, 100, price=10.0)

        pres_svc = PrescriptionService(temp_db)
        pres, items = self._make_prescription_with_item(med_id)
        pres_svc.create(pres, items)

        repo = PrescriptionRepository(temp_db)
        # 按患者名过滤
        rows = repo.find_all(patient_name='测试')
        assert len(rows) == 1
        # 不匹配的过滤
        rows = repo.find_all(patient_name='不存在')
        assert rows == []

    def test_get_statistics(self, temp_db):
        med_svc = MedicineService(temp_db)
        med_id = med_svc.create(_make_med('人参'))
        inv_svc = InventoryService(temp_db)
        inv_svc.stock_in(med_id, 100, price=10.0)

        pres_svc = PrescriptionService(temp_db)
        pres, items = self._make_prescription_with_item(med_id, qty=10, price=10.0)
        pres_svc.create(pres, items)

        repo = PrescriptionRepository(temp_db)
        stats = repo.get_statistics()
        assert stats['prescription_count'] == 1
        assert stats['total_amount'] == 100.0

    def test_get_statistics_empty(self, temp_db):
        repo = PrescriptionRepository(temp_db)
        stats = repo.get_statistics()
        assert stats == {'prescription_count': 0, 'total_amount': 0}


class TestOperationLogRepoORM:
    def test_find_all_empty(self, temp_db):
        repo = OperationLogRepository(temp_db)
        assert repo.find_all() == []

    def test_find_all_after_operation(self, temp_db):
        # 创建药材会触发 _log_operation
        svc = MedicineService(temp_db)
        svc.create(_make_med('人参'))

        repo = OperationLogRepository(temp_db)
        logs = repo.find_all()
        assert len(logs) >= 1
        # 最新日志应是 CREATE 操作
        assert logs[0]['operation_type'] == 'CREATE'
        assert logs[0]['target_type'] == 'medicine'

    def test_find_all_limit(self, temp_db):
        svc = MedicineService(temp_db)
        for i in range(5):
            svc.create(_make_med(f'药材{i}'))

        repo = OperationLogRepository(temp_db)
        logs = repo.find_all(limit=3)
        assert len(logs) == 3
