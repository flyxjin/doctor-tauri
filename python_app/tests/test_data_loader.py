# -*- coding: utf-8 -*-
"""
DataLoader 和 BuiltinDataLoader 单元测试
"""

from core.data_loader import BuiltinDataLoader
from core.services import DataLoader, MedicineService


def _make_medicine_data(name='测试药材', **kwargs):
    """构造一条符合内置数据格式的 dict"""
    defaults = dict(
        name=name,
        alias='别名',
        category='补虚药',
        nature='温',
        taste='甘',
        meridian='归脾经',
        efficacy='大补元气',
        indications='体虚欲脱',
        usage='煎服',
        dosage='3-9g',
        contraindication='实证忌服',
        quantity=100,
        unit='g',
        price=10.0,
        min_stock=20,
        notes='',
    )
    defaults.update(kwargs)
    return defaults


class TestDataLoader:
    def test_first_load_adds_medicines(self, temp_db):
        """首次加载新增药材"""
        loader = DataLoader(temp_db)
        data = [
            _make_medicine_data('人参'),
            _make_medicine_data('黄芪'),
            _make_medicine_data('当归'),
        ]

        added, updated, errors = loader.load_builtin_data(data)

        assert added == 3
        assert updated == 0
        assert errors == []

    def test_reload_without_force_skips_existing(self, temp_db):
        """重复加载（force=False）跳过已存在的"""
        loader = DataLoader(temp_db)
        data = [_make_medicine_data('人参'), _make_medicine_data('黄芪')]

        added1, _, _ = loader.load_builtin_data(data)
        assert added1 == 2

        added2, updated2, errors2 = loader.load_builtin_data(data, force=False)
        assert added2 == 0
        assert updated2 == 0
        assert errors2 == []

    def test_reload_with_force_updates_existing(self, temp_db):
        """force=True 更新已存在药材"""
        loader = DataLoader(temp_db)
        data = [_make_medicine_data('人参', efficacy='原功效', quantity=100)]
        loader.load_builtin_data(data)

        updated_data = [_make_medicine_data('人参', efficacy='新功效', quantity=200)]
        added, updated, errors = loader.load_builtin_data(updated_data, force=True)

        assert added == 0
        assert updated == 1
        assert errors == []

        med = MedicineService(temp_db).get_by_name('人参')
        assert med is not None
        assert med.efficacy == '新功效'

    def test_missing_name_skipped_with_error(self, temp_db):
        """缺少名称的记录被跳过并加入 errors"""
        loader = DataLoader(temp_db)
        data = [
            _make_medicine_data('人参'),
            {'name': '', 'category': '补虚药'},
            {'category': '清热药'},
            _make_medicine_data('黄芪'),
        ]

        added, updated, errors = loader.load_builtin_data(data)

        assert added == 2
        assert updated == 0
        assert len(errors) == 2
        assert all('缺少名称' in e for e in errors)

    def test_verify_integrity_count_mismatch(self, temp_db):
        """数量不匹配时返回错误"""
        loader = DataLoader(temp_db)
        data = [_make_medicine_data('人参'), _make_medicine_data('黄芪')]
        loader.load_builtin_data(data)

        is_valid, errors = loader.verify_data_integrity(expected_count=10)
        assert is_valid is False
        assert any('数量不匹配' in e for e in errors)

    def test_verify_integrity_count_match(self, temp_db):
        """数量匹配时返回通过"""
        loader = DataLoader(temp_db)
        data = [_make_medicine_data('人参'), _make_medicine_data('黄芪')]
        loader.load_builtin_data(data)

        is_valid, errors = loader.verify_data_integrity(expected_count=2)
        assert is_valid is True
        assert errors == []


class TestBuiltinDataLoader:
    def test_ensure_data_loaded(self, temp_db):
        """ensure_data_loaded 加载内置数据"""
        loader = BuiltinDataLoader(temp_db)
        result = loader.ensure_data_loaded()

        assert result is True
        count = temp_db.fetchone('SELECT COUNT(*) as count FROM medicines')['count']
        assert count == BuiltinDataLoader.EXPECTED_COUNT

    def test_verify_integrity_after_load(self, temp_db):
        """加载内置数据后完整性校验通过"""
        loader = BuiltinDataLoader(temp_db)
        loader.ensure_data_loaded()

        is_valid, errors = loader.verify_data_integrity()
        assert is_valid is True
        assert errors == []
