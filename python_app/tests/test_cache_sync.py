# -*- coding: utf-8 -*-
"""
缓存同步测试 - 验证 P0-2: Service 层操作后缓存自动同步
"""
from core.cache import get_medicine_cache
from core.models import Medicine
from core.services import MedicineService


def _make_medicine(name):
    return Medicine(
        name=name,
        category='补虚药',
        nature='温',
        taste='甘',
        meridian='归脾经',
        efficacy='大补元气',
        indications='体虚欲脱',
    )


class TestCacheSync:
    def test_cache_not_updated_when_uninitialized(self, temp_db):
        """缓存未初始化时，Service 操作不应报错"""
        service = MedicineService(temp_db)
        med_id = service.create(_make_medicine('未初始化药材'))

        cache = get_medicine_cache()
        assert not cache.is_initialized()
        # 缓存未初始化，get_by_id 返回 None
        assert cache.get_by_id(med_id) is None

    def test_cache_sync_on_create(self, temp_db):
        """创建药材后缓存应自动同步"""
        service = MedicineService(temp_db)

        # 初始化缓存
        cache = get_medicine_cache()
        cache.initialize([])
        assert cache.is_initialized()

        med_id = service.create(_make_medicine('缓存创建药材'))

        cached = cache.get_by_id(med_id)
        assert cached is not None
        assert cached['name'] == '缓存创建药材'

    def test_cache_sync_on_update(self, temp_db):
        """更新药材后缓存应自动同步"""
        service = MedicineService(temp_db)

        med = _make_medicine('缓存更新药材')
        med_id = service.create(med)

        # 初始化缓存（加载现有数据）
        cache = get_medicine_cache()
        cache.initialize(service.get_all_as_dicts())
        assert cache.get_by_id(med_id) is not None

        # 更新药材
        med.id = med_id
        med.efficacy = '更新后的功效'
        service.update(med)

        cached = cache.get_by_id(med_id)
        assert cached is not None
        assert cached['efficacy'] == '更新后的功效'

    def test_cache_sync_on_delete(self, temp_db):
        """删除药材后缓存应自动同步"""
        service = MedicineService(temp_db)

        med_id = service.create(_make_medicine('缓存删除药材'))

        cache = get_medicine_cache()
        cache.initialize(service.get_all_as_dicts())
        assert cache.get_by_id(med_id) is not None

        service.delete(med_id)

        assert cache.get_by_id(med_id) is None
