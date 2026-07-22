# -*- coding: utf-8 -*-
"""
Repository 写方法单元测试

覆盖：
- MedicineRepository: insert_medicine, update_medicine, delete_by_id（级联删除 4 张表）,
  insert_with_inventory, update_with_inventory
- InventoryRepository: update_stock, insert_history, update_price, update_min_stock,
  adjust_stock
- PrescriptionRepository: insert_prescription, insert_item,
  delete_items_by_prescription, delete_by_id
"""

from core.models import Medicine, Prescription, PrescriptionItem
from core.repositories import (
    InventoryRepository,
    MedicineRepository,
    PrescriptionRepository,
)


def _make_med(name, **kw):
    """构造一个最小可用的 Medicine dataclass。"""
    defaults = dict(
        name=name, alias='', category='补虚药', nature='温', taste='甘',
        meridian='归脾经', efficacy='补气', indications='体虚',
        usage='', dosage='', contraindication='', notes='',
    )
    defaults.update(kw)
    return Medicine(**defaults)


def _make_prescription(total_amount=50.0, **kw):
    """构造一个最小可用的 Prescription dataclass。"""
    defaults = dict(
        patient_name='测试患者', patient_age=30, patient_gender='男',
        diagnosis='测试诊断', total_amount=total_amount, created_by='医生',
    )
    defaults.update(kw)
    return Prescription(**defaults)


def _make_item(prescription_id, medicine_id, medicine_name='测试药材',
               quantity=10, unit='g', price=5.0):
    return PrescriptionItem(
        prescription_id=prescription_id,
        medicine_id=medicine_id,
        medicine_name=medicine_name,
        quantity=quantity,
        unit=unit,
        price=price,
        amount=quantity * price,
    )


# ====================================================================
# MedicineRepository 写方法
# ====================================================================
class TestMedicineRepoWrites:
    def test_insert_medicine_then_find_by_id(self, temp_db):
        repo = MedicineRepository(temp_db)
        med = _make_med('人参')

        med_id = repo.insert_medicine(med)

        assert isinstance(med_id, int) and med_id > 0
        row = repo.find_by_id(med_id)
        assert row is not None
        assert row['name'] == '人参'
        assert row['category'] == '补虚药'
        # insert_medicine 应同时初始化库存记录
        assert row['quantity'] == 0
        assert row['unit'] == 'g'
        assert row['price'] == 0

    def test_update_medicine_updates_fields(self, temp_db):
        repo = MedicineRepository(temp_db)
        med_id = repo.insert_medicine(_make_med('黄芪'))

        updated = _make_med(
            '黄芪',
            alias='黄耆',
            category='补气药',
            nature='微温',
            taste='甘',
            meridian='归脾肺经',
            efficacy='补气升阳',
            indications='气虚乏力',
            usage='煎服',
            dosage='9-30g',
            contraindication='实证忌用',
            notes='常用补气药',
        )
        updated.id = med_id
        repo.update_medicine(updated)

        row = repo.find_by_id(med_id)
        assert row is not None
        assert row['name'] == '黄芪'  # update_medicine 也更新 name
        assert row['alias'] == '黄耆'
        assert row['category'] == '补气药'
        assert row['nature'] == '微温'
        assert row['efficacy'] == '补气升阳'
        assert row['indications'] == '气虚乏力'
        assert row['usage'] == '煎服'
        assert row['dosage'] == '9-30g'
        assert row['contraindication'] == '实证忌用'
        assert row['notes'] == '常用补气药'

    def test_delete_by_id_cascades_four_tables(self, temp_db):
        med_repo = MedicineRepository(temp_db)
        inv_repo = InventoryRepository(temp_db)
        pres_repo = PrescriptionRepository(temp_db)

        # 1. 建药材（同时建 inventory）
        med_id = med_repo.insert_medicine(_make_med('当归'))

        # 2. 写一条 inventory_history
        inv_repo.insert_history(
            medicine_id=med_id, medicine_name='当归',
            type_='入库', quantity=100, price=10.0,
        )

        # 3. 建处方 + 引用该药材的明细
        pres_id = pres_repo.insert_prescription(_make_prescription(total_amount=50.0))
        pres_repo.insert_item(_make_item(pres_id, med_id, medicine_name='当归'))

        # 断言前置数据存在
        assert temp_db.fetchone(
            'SELECT id FROM medicines WHERE id = ?', (med_id,)
        ) is not None
        assert temp_db.fetchone(
            'SELECT id FROM inventory WHERE medicine_id = ?', (med_id,)
        ) is not None
        assert temp_db.fetchone(
            'SELECT id FROM inventory_history WHERE medicine_id = ?', (med_id,)
        ) is not None
        assert temp_db.fetchone(
            'SELECT id FROM prescription_items WHERE medicine_id = ?', (med_id,)
        ) is not None

        # 4. 执行级联删除
        med_repo.delete_by_id(med_id)

        # 5. 四张表都应该没有该 med_id 的记录
        assert temp_db.fetchone(
            'SELECT id FROM medicines WHERE id = ?', (med_id,)
        ) is None
        assert temp_db.fetchone(
            'SELECT id FROM inventory WHERE medicine_id = ?', (med_id,)
        ) is None
        assert temp_db.fetchone(
            'SELECT id FROM inventory_history WHERE medicine_id = ?', (med_id,)
        ) is None
        assert temp_db.fetchone(
            'SELECT id FROM prescription_items WHERE medicine_id = ?', (med_id,)
        ) is None
        # 处方主表本身不应被删（delete_by_id 只级联处方明细）
        assert pres_repo.find_by_id(pres_id) is not None

    def test_insert_with_inventory_creates_both(self, temp_db):
        repo = MedicineRepository(temp_db)
        item = {
            'name': '熟地黄',
            'alias': '熟地',
            'category': '补血药',
            'nature': '微温',
            'taste': '甘',
            'meridian': '归肝肾经',
            'efficacy': '补血滋阴',
            'indications': '血虚萎黄',
            'usage': '煎服',
            'dosage': '9-30g',
            'contraindication': '',
            'notes': '补血要药',
            'quantity': 200,
            'unit': 'g',
            'price': 8.5,
            'min_stock': 50,
        }

        med_id = repo.insert_with_inventory(item)
        assert isinstance(med_id, int) and med_id > 0

        # 验证药材
        med_row = repo.find_by_id(med_id)
        assert med_row is not None
        assert med_row['name'] == '熟地黄'
        assert med_row['alias'] == '熟地'
        assert med_row['category'] == '补血药'

        # 验证库存（应与传入 dict 一致，而非默认 0）
        inv_repo = InventoryRepository(temp_db)
        inv_row = inv_repo.find_by_medicine_id(med_id)
        assert inv_row is not None
        assert inv_row['quantity'] == 200
        assert inv_row['unit'] == 'g'
        assert inv_row['price'] == 8.5
        assert inv_row['min_stock'] == 50

    def test_update_with_inventory_updates_both(self, temp_db):
        repo = MedicineRepository(temp_db)
        inv_repo = InventoryRepository(temp_db)

        med_id = repo.insert_with_inventory({
            'name': '白术', 'alias': '', 'category': '补气药',
            'nature': '温', 'taste': '苦甘', 'meridian': '归脾胃经',
            'efficacy': '健脾益气', 'indications': '脾虚食少',
            'usage': '', 'dosage': '', 'contraindication': '', 'notes': '',
            'quantity': 50, 'unit': 'g', 'price': 5.0, 'min_stock': 10,
        })

        # 更新药材与库存
        repo.update_with_inventory(med_id, {
            'alias': '于术',
            'category': '补虚药',
            'nature': '温',
            'taste': '苦甘',
            'meridian': '归脾胃经',
            'efficacy': '健脾益气燥湿',
            'indications': '脾虚泄泻',
            'usage': '煎服',
            'dosage': '6-12g',
            'contraindication': '阴虚内热忌用',
            'notes': '更新后',
            'quantity': 80,
            'unit': 'g',
            'price': 7.5,
            'min_stock': 20,
        })

        med_row = repo.find_by_id(med_id)
        assert med_row is not None
        assert med_row['alias'] == '于术'
        assert med_row['efficacy'] == '健脾益气燥湿'
        assert med_row['indications'] == '脾虚泄泻'
        assert med_row['dosage'] == '6-12g'
        assert med_row['notes'] == '更新后'

        inv_row = inv_repo.find_by_medicine_id(med_id)
        assert inv_row is not None
        assert inv_row['quantity'] == 80
        assert inv_row['price'] == 7.5
        assert inv_row['min_stock'] == 20


# ====================================================================
# InventoryRepository 写方法
# ====================================================================
class TestInventoryRepoWrites:
    def test_update_stock_updates_quantity(self, temp_db):
        med_repo = MedicineRepository(temp_db)
        inv_repo = InventoryRepository(temp_db)
        med_id = med_repo.insert_medicine(_make_med('甘草'))

        # 初始 quantity=0
        inv_row = inv_repo.find_by_medicine_id(med_id)
        assert inv_row['quantity'] == 0

        # 只更新数量
        inv_repo.update_stock(med_id, 100)
        inv_row = inv_repo.find_by_medicine_id(med_id)
        assert inv_row['quantity'] == 100
        assert inv_row['price'] == 0  # 未传 price，不变

        # 同时更新数量和价格
        inv_repo.update_stock(med_id, 80, price=12.5)
        inv_row = inv_repo.find_by_medicine_id(med_id)
        assert inv_row['quantity'] == 80
        assert inv_row['price'] == 12.5

    def test_insert_history_writes_record(self, temp_db):
        med_repo = MedicineRepository(temp_db)
        inv_repo = InventoryRepository(temp_db)
        med_id = med_repo.insert_medicine(_make_med('川芎'))

        inv_repo.insert_history(
            medicine_id=med_id, medicine_name='川芎',
            type_='入库', quantity=100, price=10.0,
            total_amount=1000.0, operator='测试员', notes='首次入库',
        )

        history = inv_repo.find_history(med_id)
        assert len(history) == 1
        row = history[0]
        assert row['medicine_id'] == med_id
        assert row['medicine_name'] == '川芎'
        assert row['type'] == '入库'
        assert row['quantity'] == 100
        assert row['price'] == 10.0
        assert row['total_amount'] == 1000.0
        assert row['operator'] == '测试员'
        assert row['notes'] == '首次入库'

    def test_update_price(self, temp_db):
        med_repo = MedicineRepository(temp_db)
        inv_repo = InventoryRepository(temp_db)
        med_id = med_repo.insert_medicine(_make_med('茯苓'))

        inv_repo.update_price(med_id, 15.8)
        inv_row = inv_repo.find_by_medicine_id(med_id)
        assert inv_row['price'] == 15.8

    def test_update_min_stock(self, temp_db):
        med_repo = MedicineRepository(temp_db)
        inv_repo = InventoryRepository(temp_db)
        med_id = med_repo.insert_medicine(_make_med('泽泻'))

        inv_repo.update_min_stock(med_id, 30)
        inv_row = inv_repo.find_by_medicine_id(med_id)
        assert inv_row['min_stock'] == 30

    def test_adjust_stock_updates_quantity_only(self, temp_db):
        med_repo = MedicineRepository(temp_db)
        inv_repo = InventoryRepository(temp_db)
        med_id = med_repo.insert_medicine(_make_med('柴胡'))

        inv_repo.adjust_stock(med_id, 50)
        inv_row = inv_repo.find_by_medicine_id(med_id)
        assert inv_row['quantity'] == 50
        assert inv_row['price'] == 0
        assert inv_row['min_stock'] == 0

    def test_adjust_stock_with_price_and_min_stock(self, temp_db):
        med_repo = MedicineRepository(temp_db)
        inv_repo = InventoryRepository(temp_db)
        med_id = med_repo.insert_medicine(_make_med('桔梗'))

        inv_repo.adjust_stock(med_id, 60, price=9.9, min_stock=15)
        inv_row = inv_repo.find_by_medicine_id(med_id)
        assert inv_row['quantity'] == 60
        assert inv_row['price'] == 9.9
        assert inv_row['min_stock'] == 15


# ====================================================================
# PrescriptionRepository 写方法
# ====================================================================
class TestPrescriptionRepoWrites:
    def test_insert_prescription_and_insert_item(self, temp_db):
        med_repo = MedicineRepository(temp_db)
        pres_repo = PrescriptionRepository(temp_db)

        med_id = med_repo.insert_medicine(_make_med('丹参'))
        pres = _make_prescription(total_amount=50.0)

        pres_id = pres_repo.insert_prescription(pres)
        assert isinstance(pres_id, int) and pres_id > 0

        # 处方主表能查到
        row = pres_repo.find_by_id(pres_id)
        assert row is not None
        assert row['patient_name'] == '测试患者'
        assert row['diagnosis'] == '测试诊断'
        assert row['total_amount'] == 50.0

        # 插入明细
        item = _make_item(pres_id, med_id, medicine_name='丹参',
                          quantity=10, price=5.0)
        pres_repo.insert_item(item)

        items = pres_repo.find_items(pres_id)
        assert len(items) == 1
        assert items[0]['prescription_id'] == pres_id
        assert items[0]['medicine_id'] == med_id
        assert items[0]['medicine_name'] == '丹参'
        assert items[0]['quantity'] == 10
        assert items[0]['price'] == 5.0
        assert items[0]['amount'] == 50.0

    def test_delete_items_by_prescription_removes_all_items(self, temp_db):
        med_repo = MedicineRepository(temp_db)
        pres_repo = PrescriptionRepository(temp_db)

        # 建两味药材
        med_id1 = med_repo.insert_medicine(_make_med('黄连'))
        med_id2 = med_repo.insert_medicine(_make_med('黄芩'))

        # 建处方 + 两条明细
        pres_id = pres_repo.insert_prescription(_make_prescription(total_amount=30.0))
        pres_repo.insert_item(_make_item(pres_id, med_id1, medicine_name='黄连',
                                         quantity=3, price=5.0))
        pres_repo.insert_item(_make_item(pres_id, med_id2, medicine_name='黄芩',
                                         quantity=3, price=5.0))

        # 前置断言：有 2 条明细
        assert len(pres_repo.find_items(pres_id)) == 2

        # 执行删除
        pres_repo.delete_items_by_prescription(pres_id)

        # 明细应全部被删
        assert pres_repo.find_items(pres_id) == []
        # 处方主表本身不应被删
        assert pres_repo.find_by_id(pres_id) is not None

    def test_delete_by_id_removes_prescription(self, temp_db):
        pres_repo = PrescriptionRepository(temp_db)
        pres_id = pres_repo.insert_prescription(_make_prescription())

        assert pres_repo.find_by_id(pres_id) is not None
        pres_repo.delete_by_id(pres_id)
        assert pres_repo.find_by_id(pres_id) is None
