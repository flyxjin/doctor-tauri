# -*- coding: utf-8 -*-
"""
端到端集成测试

覆盖核心业务流程的完整链路：
1. 药材管理：新增 → 搜索 → 编辑 → 删除
2. 库存管理：入库 → 出库 → 库存预警
3. 处方开具：添加药材 → 保存处方 → 库存扣减
4. 处方查询：按日期/患者查询 → 删除处方 → 库存恢复
5. 统计报表：销售统计 → 趋势数据
6. 缓存一致性：写操作后缓存同步验证
7. 事务原子性：多表操作失败回滚验证
"""
from datetime import datetime

import pytest

from core import (
    Database,
    InventoryService,
    Medicine,
    MedicineService,
    Prescription,
    PrescriptionItem,
    PrescriptionService,
)
from core.cache import get_medicine_cache, invalidate_medicine_cache


@pytest.fixture
def fresh_db():
    """每个测试用独立的数据库"""
    import os
    import tempfile
    fd, path = tempfile.mkstemp(suffix='.db')
    os.close(fd)
    Database.reset_instance()
    db = Database(path)
    yield db
    db.close()
    Database.reset_instance()
    if os.path.exists(path):
        os.unlink(path)


@pytest.fixture
def services(fresh_db):
    """初始化所有 Service"""
    invalidate_medicine_cache()
    return {
        'db': fresh_db,
        'medicine': MedicineService(fresh_db),
        'inventory': InventoryService(fresh_db),
        'prescription': PrescriptionService(fresh_db),
    }


def _make_medicine(name='测试药材', category='补虚药', nature='温'):
    return Medicine(
        name=name, alias=f'{name}别名', category=category, nature=nature,
        taste='甘', meridian='脾经', efficacy='测试功效', indications='测试主治',
        usage='水煎服', dosage='3-9g', contraindication='无', notes=''
    )


def _find_inventory(inv_svc, medicine_id):
    """从 get_all 结果中找到指定 medicine_id 的库存"""
    items = inv_svc.get_all()
    for item in items:
        if item.medicine_id == medicine_id:
            return item
    return None


class TestMedicineManagementFlow:
    """药材管理端到端流程"""

    def test_create_search_edit_delete(self, services):
        med_svc = services['medicine']

        # 1. 新增药材
        med = _make_medicine('当归')
        med_id = med_svc.create(med)
        assert med_id is not None

        # 2. 搜索验证
        results = med_svc.search('当归')
        assert len(results) == 1
        assert results[0].name == '当归'

        # 3. 编辑药材
        med.id = med_id
        med.alias = '当归尾'
        med_svc.update(med)
        updated = med_svc.get_by_id(med_id)
        assert updated.alias == '当归尾'

        # 4. 删除药材
        med_svc.delete(med_id)
        assert med_svc.get_by_id(med_id) is None

    def test_duplicate_name_rejected(self, services):
        med_svc = services['medicine']
        med_svc.create(_make_medicine('黄芪'))
        with pytest.raises(Exception):
            med_svc.create(_make_medicine('黄芪'))

    def test_category_loaded_from_db(self, services):
        """分类下拉数据源验证"""
        med_svc = services['medicine']
        med_svc.create(_make_medicine('人参', category='补虚药'))
        med_svc.create(_make_medicine('黄连', category='清热药'))
        categories = med_svc.get_categories()
        assert '补虚药' in categories
        assert '清热药' in categories


class TestInventoryFlow:
    """库存管理端到端流程"""

    def test_stock_in_out_and_low_stock(self, services):
        med_svc = services['medicine']
        inv_svc = services['inventory']

        med_id = med_svc.create(_make_medicine('甘草'))

        # 入库 1000g
        inv_svc.stock_in(med_id, 1000, price=30.0, operator='测试员')
        inv = _find_inventory(inv_svc, med_id)
        assert inv.quantity == 1000

        # 出库 200g
        inv_svc.stock_out(med_id, 200, operator='测试员')
        inv = _find_inventory(inv_svc, med_id)
        assert inv.quantity == 800

        # 低库存预警（设置 min_stock=900）
        inv_svc.update_min_stock(med_id, 900)
        low = inv_svc.get_low_stock_items()
        assert any(item.medicine_id == med_id for item in low)

    def test_insufficient_stock_rejected(self, services):
        med_svc = services['medicine']
        inv_svc = services['inventory']
        med_id = med_svc.create(_make_medicine('茯苓'))
        inv_svc.stock_in(med_id, 100, price=20.0, operator='测试')

        with pytest.raises(Exception):
            inv_svc.stock_out(med_id, 200, operator='测试')


class TestPrescriptionFlow:
    """处方开具端到端流程"""

    def test_create_prescription_with_items(self, services):
        med_svc = services['medicine']
        inv_svc = services['inventory']
        pres_svc = services['prescription']

        # 准备药材和库存
        renshen_id = med_svc.create(_make_medicine('人参'))
        huangqi_id = med_svc.create(_make_medicine('黄芪'))
        inv_svc.stock_in(renshen_id, 500, price=100, operator='测试')
        inv_svc.stock_in(huangqi_id, 500, price=50, operator='测试')

        # 开处方（items 作为单独参数）
        pres = Prescription(
            patient_name='张三', patient_age=45, patient_gender='男',
            diagnosis='气虚'
        )
        items = [
            PrescriptionItem(
                prescription_id=0, medicine_id=renshen_id, medicine_name='人参',
                quantity=10, unit='g', price=100, amount=1000
            ),
            PrescriptionItem(
                prescription_id=0, medicine_id=huangqi_id, medicine_name='黄芪',
                quantity=15, unit='g', price=50, amount=750
            ),
        ]
        pres_id = pres_svc.create(pres, items)
        assert pres_id is not None

        # 验证库存已扣减
        inv1 = _find_inventory(inv_svc, renshen_id)
        inv2 = _find_inventory(inv_svc, huangqi_id)
        assert inv1.quantity == 490
        assert inv2.quantity == 485

    def test_delete_prescription_restores_stock(self, services):
        med_svc = services['medicine']
        inv_svc = services['inventory']
        pres_svc = services['prescription']

        baihu_id = med_svc.create(_make_medicine('白术'))
        inv_svc.stock_in(baihu_id, 200, price=40, operator='测试')

        pres = Prescription(patient_name='李四', patient_age=30, diagnosis='脾虚')
        items = [
            PrescriptionItem(
                prescription_id=0, medicine_id=baihu_id, medicine_name='白术',
                quantity=20, unit='g', price=40, amount=800
            )
        ]
        pres_id = pres_svc.create(pres, items)

        # 删除处方应恢复库存
        pres_svc.delete(pres_id)
        inv = _find_inventory(inv_svc, baihu_id)
        assert inv.quantity == 200

    def test_prescription_date_filter(self, services):
        pres_svc = services['prescription']
        today = datetime.now().strftime('%Y-%m-%d')

        # 创建两条处方
        for name in ['患者A', '患者B']:
            pres = Prescription(patient_name=name, patient_age=30, diagnosis='测试')
            pres_svc.create(pres, [])

        results = pres_svc.get_all(start_date=today, end_date=today)
        assert len(results) == 2

        results = pres_svc.get_all(patient_name='患者A')
        assert len(results) == 1


class TestCacheConsistency:
    """缓存一致性验证"""

    def test_cache_synced_after_create(self, services):
        med_svc = services['medicine']
        cache = get_medicine_cache()
        if not cache.is_initialized():
            cache.initialize(med_svc.get_all_as_dicts())

        # 新增后缓存应同步
        med_svc.create(_make_medicine('缓存测试药'))
        results = cache.search('缓存测试药')
        assert len(results) == 1

    def test_cache_synced_after_delete(self, services):
        med_svc = services['medicine']
        cache = get_medicine_cache()
        med_id = med_svc.create(_make_medicine('待删除药'))
        cache.initialize(med_svc.get_all_as_dicts())
        assert len(cache.search('待删除药')) == 1

        med_svc.delete(med_id)
        assert len(cache.search('待删除药')) == 0


class TestTransactionAtomicity:
    """事务原子性验证"""

    def test_prescription_create_atomic(self, services):
        """处方创建失败应回滚库存扣减"""
        med_svc = services['medicine']
        inv_svc = services['inventory']
        pres_svc = services['prescription']

        med_id = med_svc.create(_make_medicine('原子性测试药'))
        inv_svc.stock_in(med_id, 100, price=30, operator='测试')

        # 构造一个会失败的处方（库存不足）
        pres = Prescription(patient_name='测试', patient_age=20, diagnosis='测试')
        items = [
            PrescriptionItem(
                prescription_id=0, medicine_id=med_id, medicine_name='原子性测试药',
                quantity=999, unit='g', price=30, amount=999*30
            )
        ]

        # 创建应失败
        with pytest.raises(Exception):
            pres_svc.create(pres, items)

        # 库存不应被扣减
        inv = _find_inventory(inv_svc, med_id)
        assert inv.quantity == 100


class TestStatisticsFlow:
    """统计报表端到端流程"""

    def test_revenue_trend_after_prescription(self, services):
        med_svc = services['medicine']
        inv_svc = services['inventory']
        pres_svc = services['prescription']

        med_id = med_svc.create(_make_medicine('统计药'))
        inv_svc.stock_in(med_id, 500, price=20, operator='测试')

        pres = Prescription(patient_name='统计患者', patient_age=40, diagnosis='测试')
        pres.total_amount = 1000
        items = [
            PrescriptionItem(
                prescription_id=0, medicine_id=med_id, medicine_name='统计药',
                quantity=50, unit='g', price=20, amount=1000
            )
        ]
        pres_svc.create(pres, items)

        # 验证统计服务能查到今日营收
        today = datetime.now().strftime('%Y-%m-%d')
        trend = services['db'].fetchall(
            "SELECT date(created_at) as date, SUM(total_amount) as revenue "
            "FROM prescriptions WHERE date(created_at) = ? GROUP BY date(created_at)",
            (today,)
        )
        assert len(trend) == 1
        assert trend[0]['revenue'] == 1000
