# -*- coding: utf-8 -*-
"""
Service 层单元测试
"""
import pytest

from core.models import Medicine
from core.services import InventoryService, MedicineService, ServiceError


def _make_medicine(name='测试药材', **kwargs):
    """构造一个通过验证的药材对象"""
    defaults = dict(
        name=name,
        category='补虚药',
        nature='温',
        taste='甘',
        meridian='归脾经',
        efficacy='大补元气',
        indications='体虚欲脱',
    )
    defaults.update(kwargs)
    return Medicine(**defaults)


class TestMedicineService:
    def test_create_and_get(self, medicine_service):
        med = _make_medicine('创建人参')
        med_id = medicine_service.create(med)
        assert med_id > 0

        result = medicine_service.get_by_id(med_id)
        assert result is not None
        assert result.name == '创建人参'

    def test_create_duplicate_raises(self, medicine_service):
        medicine_service.create(_make_medicine('重复药材'))
        with pytest.raises(ServiceError):
            medicine_service.create(_make_medicine('重复药材'))

    def test_update(self, medicine_service):
        med = _make_medicine('更新药材')
        med_id = medicine_service.create(med)

        med.id = med_id
        med.efficacy = '新功效'
        medicine_service.update(med)

        result = medicine_service.get_by_id(med_id)
        assert result.efficacy == '新功效'

    def test_delete(self, medicine_service):
        med = _make_medicine('删除药材')
        med_id = medicine_service.create(med)

        medicine_service.delete(med_id)
        assert medicine_service.get_by_id(med_id) is None

    def test_search(self, medicine_service):
        medicine_service.create(_make_medicine('黄芪', efficacy='补气升阳'))
        medicine_service.create(_make_medicine('黄连', efficacy='清热燥湿'))

        results = medicine_service.search('黄')
        assert len(results) == 2

    def test_get_categories(self, medicine_service):
        medicine_service.create(_make_medicine('药材1', category='补虚药'))
        medicine_service.create(_make_medicine('药材2', category='清热药'))

        categories = medicine_service.get_categories()
        assert '补虚药' in categories
        assert '清热药' in categories


class TestInventoryService:
    def _setup_medicine(self, db, name='库存药材'):
        med_service = MedicineService(db)
        return med_service.create(_make_medicine(name))

    def test_stock_in(self, temp_db):
        med_id = self._setup_medicine(temp_db)
        inv_service = InventoryService(temp_db)

        inv_service.stock_in(med_id, 100, price=10.0)
        inv = inv_service.get_by_medicine_id(med_id)
        assert inv.quantity == 100

    def test_stock_out(self, temp_db):
        med_id = self._setup_medicine(temp_db, '出库药材')
        inv_service = InventoryService(temp_db)

        inv_service.stock_in(med_id, 100, price=10.0)
        inv_service.stock_out(med_id, 30)

        inv = inv_service.get_by_medicine_id(med_id)
        assert inv.quantity == 70

    def test_stock_out_insufficient_raises(self, temp_db):
        med_id = self._setup_medicine(temp_db, '不足药材')
        inv_service = InventoryService(temp_db)

        inv_service.stock_in(med_id, 10, price=10.0)
        with pytest.raises(ServiceError):
            inv_service.stock_out(med_id, 50)

    def test_low_stock_filter(self, temp_db):
        med_id = self._setup_medicine(temp_db, '低库存药材')
        inv_service = InventoryService(temp_db)

        inv_service.stock_in(med_id, 5, price=10.0)
        # 设置最低库存（通过直接更新）
        temp_db.execute(
            'UPDATE inventory SET min_stock = 10 WHERE medicine_id = ?',
            (med_id,)
        )

        low_stock = inv_service.get_all(low_stock_only=True)
        assert any(inv.medicine_id == med_id for inv in low_stock)
