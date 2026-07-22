# -*- coding: utf-8 -*-
"""
PrescriptionService 单元测试
"""
from datetime import datetime, timedelta

import pytest

from core.models import Medicine, Prescription, PrescriptionItem
from core.services import (
    InventoryService,
    MedicineService,
    PrescriptionService,
    ServiceError,
)


def _make_medicine(name='处方药材', **kwargs):
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


def _make_prescription(patient_name='张三', **kwargs):
    """构造一个处方对象"""
    defaults = dict(
        patient_name=patient_name,
        patient_age=30,
        patient_gender='男',
        diagnosis='气虚',
        total_amount=0.0,
        created_by='测试医生',
    )
    defaults.update(kwargs)
    return Prescription(**defaults)


def _make_item(medicine_id, medicine_name, quantity, price, unit='g'):
    """构造一个处方明细对象（prescription_id 由 Service 在创建时回填）"""
    return PrescriptionItem(
        prescription_id=0,
        medicine_id=medicine_id,
        medicine_name=medicine_name,
        quantity=quantity,
        unit=unit,
        price=price,
        amount=quantity * price,
    )


def _setup_medicine_with_stock(db, name, quantity, price=10.0):
    """创建药材并入库，返回 (medicine_id, inventory_service)"""
    med_service = MedicineService(db)
    inv_service = InventoryService(db)
    med_id = med_service.create(_make_medicine(name))
    inv_service.stock_in(med_id, quantity, price=price)
    return med_id, inv_service


class TestPrescriptionServiceCreate:
    def test_create_deducts_stock(self, temp_db):
        """创建处方后库存正确扣减"""
        med_id, inv_service = _setup_medicine_with_stock(temp_db, '扣减药材', 100, price=20.0)
        pres_service = PrescriptionService(temp_db)

        prescription = _make_prescription('扣减患者')
        items = [_make_item(med_id, '扣减药材', 30, 20.0)]
        prescription.total_amount = sum(it.amount for it in items)

        pres_id = pres_service.create(prescription, items)
        assert pres_id > 0

        inv = inv_service.get_by_medicine_id(med_id)
        assert inv.quantity == 70  # 100 - 30

    def test_create_insufficient_stock_raises(self, temp_db):
        """创建处方时库存不足抛 ServiceError"""
        med_id, _ = _setup_medicine_with_stock(temp_db, '不足药材', 10, price=5.0)
        pres_service = PrescriptionService(temp_db)

        prescription = _make_prescription('不足患者')
        items = [_make_item(med_id, '不足药材', 50, 5.0)]  # 需要 50，库存只有 10

        with pytest.raises(ServiceError):
            pres_service.create(prescription, items)

        # 库存不足应回滚，库存不应被扣减
        inv_service = InventoryService(temp_db)
        inv = inv_service.get_by_medicine_id(med_id)
        assert inv.quantity == 10  # 库存不变

    def test_create_missing_inventory_raises(self, temp_db):
        """创建处方时缺少库存记录抛 ServiceError"""
        med_service = MedicineService(temp_db)
        med_id = med_service.create(_make_medicine('无库存药材'))
        # 故意不创建库存记录

        pres_service = PrescriptionService(temp_db)
        prescription = _make_prescription('无库存患者')
        items = [_make_item(med_id, '无库存药材', 10, 5.0)]

        with pytest.raises(ServiceError):
            pres_service.create(prescription, items)

        # 处方未被创建
        assert pres_service.get_all() == []

    def test_create_multiple_items(self, temp_db):
        """多 item 处方创建"""
        med_id1, _ = _setup_medicine_with_stock(temp_db, '多味1', 100, price=10.0)
        med_id2, _ = _setup_medicine_with_stock(temp_db, '多味2', 200, price=15.0)
        med_id3, _ = _setup_medicine_with_stock(temp_db, '多味3', 50, price=8.0)

        pres_service = PrescriptionService(temp_db)
        inv_service = InventoryService(temp_db)

        items = [
            _make_item(med_id1, '多味1', 20, 10.0),
            _make_item(med_id2, '多味2', 30, 15.0),
            _make_item(med_id3, '多味3', 10, 8.0),
        ]
        prescription = _make_prescription('多味患者')
        prescription.total_amount = sum(it.amount for it in items)

        pres_id = pres_service.create(prescription, items)
        assert pres_id > 0

        # 三个药材的库存都被正确扣减
        assert inv_service.get_by_medicine_id(med_id1).quantity == 80  # 100 - 20
        assert inv_service.get_by_medicine_id(med_id2).quantity == 170  # 200 - 30
        assert inv_service.get_by_medicine_id(med_id3).quantity == 40  # 50 - 10


class TestPrescriptionServiceDelete:
    def test_delete_restores_stock(self, temp_db):
        """删除处方后库存回退"""
        med_id, _ = _setup_medicine_with_stock(temp_db, '回退药材', 100, price=12.0)
        pres_service = PrescriptionService(temp_db)
        inv_service = InventoryService(temp_db)

        items = [_make_item(med_id, '回退药材', 40, 12.0)]
        prescription = _make_prescription('回退患者')
        prescription.total_amount = sum(it.amount for it in items)

        pres_id = pres_service.create(prescription, items)
        assert inv_service.get_by_medicine_id(med_id).quantity == 60  # 100 - 40

        # 删除处方，库存应回退
        pres_service.delete(pres_id, operator='管理员')
        assert inv_service.get_by_medicine_id(med_id).quantity == 100  # 回退到 100

        # 处方已被删除
        assert pres_service.get_by_id(pres_id) is None


class TestPrescriptionServiceQuery:
    def test_get_by_id_returns_prescription_with_items(self, temp_db):
        """get_by_id 返回处方含 items"""
        med_id1, _ = _setup_medicine_with_stock(temp_db, '查询1', 100, price=10.0)
        med_id2, _ = _setup_medicine_with_stock(temp_db, '查询2', 100, price=25.0)

        pres_service = PrescriptionService(temp_db)

        items = [
            _make_item(med_id1, '查询1', 15, 10.0),
            _make_item(med_id2, '查询2', 8, 25.0),
        ]
        prescription = _make_prescription('查询患者', diagnosis='测试诊断')
        prescription.total_amount = sum(it.amount for it in items)

        pres_id = pres_service.create(prescription, items)

        result = pres_service.get_by_id(pres_id)
        assert result is not None
        assert result.id == pres_id
        assert result.patient_name == '查询患者'
        assert result.diagnosis == '测试诊断'
        # items 应被正确加载
        assert len(result.items) == 2
        item_meds = {it.medicine_name for it in result.items}
        assert item_meds == {'查询1', '查询2'}
        # 校验明细字段
        for it in result.items:
            assert it.quantity > 0
            assert it.price > 0
            assert it.amount == it.quantity * it.price

    def test_get_all_supports_date_filter(self, temp_db):
        """get_all 支持日期过滤"""
        med_id, _ = _setup_medicine_with_stock(temp_db, '过滤药材', 500, price=10.0)
        pres_service = PrescriptionService(temp_db)

        # 创建一个处方
        items = [_make_item(med_id, '过滤药材', 10, 10.0)]
        prescription = _make_prescription('今日患者')
        prescription.total_amount = sum(it.amount for it in items)
        pres_id = pres_service.create(prescription, items)

        today = datetime.now().strftime('%Y-%m-%d')
        yesterday = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
        tomorrow = (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d')

        # Repository.insert_prescription 走原始 SQL 不写 created_at，
        # 此处补一个时间戳，以便验证 get_all 的日期过滤逻辑
        temp_db.execute(
            'UPDATE prescriptions SET created_at = ? WHERE id = ?',
            (today, pres_id)
        )

        # start_date = 今天，应能查到
        results_today = pres_service.get_all(start_date=today)
        assert len(results_today) == 1
        assert results_today[0].patient_name == '今日患者'

        # end_date = 昨天，应查不到
        results_yesterday = pres_service.get_all(end_date=yesterday)
        assert len(results_yesterday) == 0

        # 范围 [今天, 明天]，应查到
        results_range = pres_service.get_all(start_date=today, end_date=tomorrow)
        assert len(results_range) == 1
